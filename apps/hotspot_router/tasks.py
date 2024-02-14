from datetime import datetime
from celery import shared_task
from librouteros.query import Key
import re

from apps.hotspot_router.models import HotspotRouter, HotspotActiveUser, HotspotHostIpMac
from system.router.ssh_router import MikroTikSSHManager
from django.db import connection as db_connection
import datetime
import logging

logger = logging.getLogger(__name__)

#not running
@shared_task
def update_hotspot_router_user():
    hotspot_router = HotspotRouter.objects.all()
    for data in hotspot_router:
        connection = MikroTikSSHManager.connect_router(data.ip_address, data.user_name,
                                                       data.password,
                                                       data.ssh_port)
        if connection:
            names = []
            try:
                stdin, stdout, stderr = connection.exec_command(
                    '/ip hotspot host; :foreach item in=[find] do={:put ({"MAC"=[get $item mac-address]; "IP"=[get $item '
                    'address]; "Comment"=[get $item comment]; "Uptime"=[get $item uptime]})}')
                output = stdout.read().decode('utf-8').split("\n")
                for line in output:
                    pairs = line.split(';')
                    data_dict = {}
                    for pair in pairs:
                        key, value = pair.split('=')
                        data_dict[key] = value.replace('\r', '')

                    if data_dict.get('Comment'):
                        pattern = r'\b\d{11}\b'
                        matches = re.findall(pattern, data_dict.get('Comment'))
                        if matches:
                            names.append({str(data_dict.get('Comment')): data_dict})
            except Exception as e:
                print(str(e))
            hotspot_active_user = HotspotActiveUser.objects.filter(router_id=data.id).first()
            if hotspot_active_user:
                hotspot_active_user.user_list = names
                hotspot_active_user.save()
            else:
                hotspot_active_user = HotspotActiveUser()
                hotspot_active_user.user_list = names
                hotspot_active_user.router_id = data.id
                hotspot_active_user.save()


@shared_task()
def update_hotspot_mac_ip():
    hotspot_router = HotspotRouter.objects.all()
    model_name = HotspotHostIpMac._meta.db_table
    with db_connection.cursor() as cursor:
        cursor.execute(f'TRUNCATE TABLE {model_name};')

    for data in hotspot_router:
        print(data.id)
        connection = MikroTikSSHManager.connect_router(data.ip_address, data.user_name,
                                                       data.password,
                                                       data.ssh_port)
        if connection:
            try:
                stdin, stdout, stderr = connection.exec_command(
                    '/ip hotspot host; :foreach item in=[find] do={:put ({"MAC"=[get $item mac-address]; "IP"=[get $item '
                    'address]; "Comment"=[get $item comment]; "Server"=[get $item server]; "Uptime"=[get $item uptime]})}')
                output = stdout.read().decode('utf-8').split("\n")
                data_list = []
                for line in output:
                    if line:
                        pairs = line.split(';')
                        data_dict = {}
                        for pair in pairs:
                            try:
                                key, value = pair.split('=')
                                data_dict[key] = value
                            except ValueError:
                                print(f"Error splitting pair: {pair}")
                        if data_dict:
                            comment = ''
                            if data_dict.get('Comment'):
                                pattern = r'\b\d{11}\b'
                                matches = re.findall(pattern, data_dict.get('Comment'))
                                if matches:
                                    comment = data_dict.get('Comment')
                                else:
                                    comment = ''
                            new_data_dict = {
                                'mac_address': data_dict.get('MAC'),
                                'ip_address': data_dict.get('IP'),
                                'server': data_dict.get('Server'),
                                'router_id': data.id,
                                'comment': comment,

                            }
                            data_list.append(new_data_dict)
                        else:
                            data_list.append('')
                if len(data_list) > 0:
                    instances = []
                    for value in data_list:
                        if isinstance(value, dict):
                            instance = HotspotHostIpMac(**value)
                            instances.append(instance)

                    if instances:
                        HotspotHostIpMac.objects.bulk_create(instances)

            except Exception as e:
                print(str(e),'error')

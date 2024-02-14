import logging
from datetime import datetime

from celery import shared_task
from system.router.ssh_router import MikroTikSSHManager
from .models import HotspotCustomer
from ..config.models import GeneralAdminConfig
from ..hotspot_router.models import UserHotspotRouter, HotspotRouter
import re
import logging

logger = logging.getLogger(__name__)


@shared_task()
def ssh_router_user_add_remove():
    print('ok')
    router_list = HotspotRouter.objects.all()
    try:
        for data in router_list:
            remove_customer = set()
            add_customer = []
            connection = MikroTikSSHManager.connect_router(data.ip_address, data.user_name,
                                                           data.password,
                                                           data.ssh_port)
            if connection:
                user_list = get_customer_list_by_router(connection)
                admin_id = set()
                seller_data = UserHotspotRouter.objects.filter(router_list__icontains=str(data.id)).all()
                if seller_data:
                    for seller in seller_data:
                        admin_id.add(seller.seller.user_id)
                admin_data = GeneralAdminConfig.objects.filter(hotspot_router_list__icontains=str(data.id)).all()
                if admin_data:
                    for item in admin_data:
                        admin_id.add(item.admin_id)
                customer_data = HotspotCustomer.objects.filter(admin_id__in=admin_id).all()
                for value in customer_data:
                    mobile = value.mobile[3:]
                    if value.package_expire_date < datetime.now():
                        if user_list:
                            if mobile == '01831616363':
                                pass
                            if mobile in user_list:
                                remove_customer.add(value.mobile)
                    elif value.package_expire_date > datetime.now():
                        if mobile not in user_list:
                            if len(mobile) == 11:
                                if value.mac_address:
                                    add_customer.append({
                                        'mobile': mobile,
                                        'mac_address': str(value.mac_address)
                                    })
                if add_customer:
                    command = ''
                    for username in add_customer:
                        if username.get("mobile").startswith("+88"):
                            username['mobile'] = username.get("mobile")[3:]
                        command += (f'/ip hotspot ip-binding add comment="{username.get("mobile")}" '
                                    f'mac-address={username.get("mac_address")} type=bypassed; ')
                    connection.exec_command(command)
                if remove_customer:
                    command = ''
                    active_remove = ''
                    for username in remove_customer:
                        if username.startswith("+88"):
                            username = username[3:]
                        command += f'ip hotspot ip-binding remove [find comment ={username}]; '
                    connection.exec_command(command)
                    connection.exec_command(active_remove)

    except Exception as e:
        print(str(e))


@shared_task()
def update_hotspot_customer_mac():
    router_list = HotspotRouter.objects.all()

    try:
        for data in router_list:
            update_customer_mac = []
            connection = MikroTikSSHManager.connect_router(data.ip_address, data.user_name,
                                                           data.password,
                                                           data.ssh_port)
            if connection:
                user_list = get_hotspot_bound_by_router(connection)
                admin_id = set()

                seller_data = UserHotspotRouter.objects.filter(router_list__icontains=str(data.id)).all()
                if seller_data:
                    for seller in seller_data:
                        admin_id.add(seller.seller.user_id)

                admin_data = GeneralAdminConfig.objects.filter(hotspot_router_list__icontains=str(data.id)).all()
                if admin_data:
                    for item in admin_data:
                        admin_id.add(item.admin_id)

                customer_data = HotspotCustomer.objects.filter(admin_id__in=admin_id).all()
                for value in customer_data:
                    mobile = value.mobile[3:]
                    if value.package_expire_date > datetime.now():
                        if mobile in user_list:
                            ip_bind_mac = user_list.get(mobile).replace('\r', '')
                            if ip_bind_mac != value.mac_address:
                                if len(mobile) == 11:
                                    update_customer_mac.append({
                                        'mobile': mobile,
                                        'mac_address': str(value.mac_address)
                                    })

                if update_customer_mac:
                    command = ''
                    for username in update_customer_mac:
                        if username.get("mobile").startswith("+88"):
                            username['mobile'] = username.get("mobile")[3:]
                        command += (f'ip hotspot ip-binding set mac-address={username.get("mac_address")} '
                                    f'[find comment ={username.get("mobile")}]; ')
                    connection.exec_command(command)
            else:
                continue
    except Exception as e:
        print(str(e))


def get_customer_list_by_router(connection):
    try:
        stdin, stdout, stderr = connection.exec_command('ip hotspot ip-binding print')

        output = stdout.read().decode('utf-8').split("\n")
        names = []
        for line in output:
            pattern = r'\b\d{11}\b'
            matches = re.findall(pattern, line)
            if matches:
                names.append(matches[0])
        return names

    except Exception as e:
        print(str(e))


def get_hotspot_bound_by_router(connection):
    try:
        stdin, stdout, stderr = connection.exec_command(
            'ip hotspot ip-binding; :foreach item in=[find] do={ :put ({"MAC"=[get $item mac-address]; "Comment"=[get $item comment]})}; ')

        output = stdout.read().decode('utf-8').split("\n")
        names = {}
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
                names[data_dict.get('Comment')] = data_dict.get('MAC')

        return names

    except Exception as e:
        print(str(e))

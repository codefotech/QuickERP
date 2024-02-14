import re
from datetime import datetime

from celery import shared_task

from apps.config.models import GeneralAdminConfig
from apps.package.models import Package
from apps.pppoe_customer.models import PPPOECustomer
from apps.router.models import Router
from apps.seller.models import Seller
from system.router.ssh_router import MikroTikSSHManager


@shared_task
def update_pppoe_customer_package():
    router_list = Router.objects.filter(id=2).all()
    package_dict = {}
    package_list = Package.objects.all()
    for package in package_list:
        package_dict[package.id] = package.profile

    try:
        for data in router_list:
            expired_customer = set()
            add_customer = []
            update_customer = []
            connection = MikroTikSSHManager.connect_router(data.ip_address, data.user_name,
                                                           data.password,
                                                           data.ssh_port)
            if connection:
                user_list = get_pppoe_list_by_router(connection)
                admin_id = set()
                seller = Seller.objects.filter(router_id=data.id).all()
                for seller_data in seller:
                    admin_id.add(seller_data.user_id)
                admin_datas = GeneralAdminConfig.objects.filter(router_list__icontains=str(data.id)).all()
                for admin_data in admin_datas:
                    admin_id.add(admin_data.admin_id)
                pppoe_customer = PPPOECustomer.objects.filter(admin_id__in=admin_id).all()
                for customer in pppoe_customer:
                    if customer.expire_at < datetime.now():
                        expired_customer.add(customer.pppoe_user)
                    elif customer.expire_at > datetime.now():
                        if customer.pppoe_user not in user_list:
                            add_customer.append({
                                'username': customer.pppoe_user,
                                'password': customer.pppoe_password,
                                'profile': package_dict.get(customer.package_id),

                            })
                        else:
                            update_customer.append({
                                'username': customer.pppoe_user,
                                'profile': package_dict.get(customer.package_id)
                            })
                if add_customer:
                    command = ''
                    for username in add_customer:
                        command += (
                            f'ppp secret add name={username.get("username")} password={username.get("password")}'
                            f' profile={username.get("profile")} service=pppoe; ')
                    connection.exec_command(command)

                if update_customer:
                    update_command = ''
                    for username in update_customer:
                        update_command += (
                            f'/ppp secret set [find name={username.get("username")}] profile={username.get("profile")} '
                            f'service=pppoe; ')
                    connection.exec_command(update_command)

                if expired_customer:
                    expired_command = ''
                    for username in expired_customer:
                        expired_command += (
                            f'/ppp secret set [find name={username}] profile=off service=pppoe; ')
                    connection.exec_command(expired_command)

    except Exception as e:
        print(str(e))


def get_pppoe_list_by_router(connection):
    try:
        stdin, stdout, stderr = connection.exec_command('/ppp secret print detail')

        output = stdout.read().decode('utf-8').split(";;;")
        names = []
        for line in output:
            pattern = r'name="([^"]+)"'
            match = re.search(pattern, line)
            if match:
                names.append(match.group(1))

        return names

    except Exception as e:
        print(str(e))

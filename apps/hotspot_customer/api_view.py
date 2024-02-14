import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.config.models import GeneralAdminConfig
from apps.hotspot_router.models import UserHotspotRouter, HotspotRouter, HotspotHostIpMac
from apps.seller.models import Seller
from apps.user.models import Users
from system.all_utils.ip_address import ip_address_check_with_subnet
from system.auth.api import token_required
from apps.hotspot_customer.models import HotspotCustomer, HotspotCustomerToken
from datetime import datetime, timedelta, timezone
import random

from system.router.connect import MikroTikManager
from system.router.ssh_router import MikroTikSSHManager
from system.sms.send_sms import send_sms
import jwt
from django.conf import settings
from librouteros.query import Key


@csrf_exempt
def customer_create_or_otp_send(request):
    try:
        if 'mobile' not in request.POST:
            response_data = {
                'status': 'error',
                'message': 'Mobile number is missing in the request'
            }
            return JsonResponse(response_data, status=400)
        if request.POST.get('mobile'):
            mobile = request.POST.get('mobile')
            if mobile.startswith("+88"):
                mobile = mobile[3:]
                if not len(mobile) == 11:
                    response_data = {
                        'status': 'error',
                        'message': 'Invalid Mobile Number'
                    }
                    return JsonResponse(response_data, status=400)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Invalid Mobile Number'
                }
                return JsonResponse(response_data, status=400)

        request_number = request.POST.get('mobile')
        customer = HotspotCustomer.objects.filter(mobile=request_number).first()

        gate_way = request.POST.get('gateway')
        ip_address = request.POST.get('wifi_ip')
        if gate_way and ip_address:
            hotspot_host_ip = HotspotHostIpMac.objects.filter(ip_address=ip_address).first()
            if hotspot_host_ip:
                mac_address = hotspot_host_ip.mac_address
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Wrong wireless network connected'
                }
                return JsonResponse(response_data, status=404)

            seller = Seller.objects.filter(subnet_mask=gate_way).first()
            admin_config = GeneralAdminConfig.objects.filter(subnet_mask=gate_way).first()
            if seller:
                admin_id = seller.user_id
            elif admin_config:
                admin_id = admin_config.admin_id
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Wrong wireless network connected'
                }
                return JsonResponse(response_data, status=404)

            if customer:
                otp_code = random.randint(1000, 9999)
                customer.otp_token = otp_code
                customer.otp_expire_time = datetime.now() + timedelta(minutes=4)
                customer.save()

            else:
                if HotspotCustomer.objects.last():
                    customer_id = HotspotCustomer.objects.last().pk + random.randint(111, 1000000000)
                else:
                    customer_id = 101 + random.randint(111, 1000000000)
                otp_code = random.randint(1000, 9999)
                print(otp_code)
                HotspotCustomer.objects.create(
                    name=f'Hotspot-Customer-{customer_id}',
                    mobile=request_number,
                    admin_id=admin_id,
                    otp_token=otp_code,
                    otp_expire_time=datetime.now() + timedelta(minutes=4),
                    mac_address=mac_address
                )
            messages = f'Your OTP code is {otp_code}'
            send_sms(request_number, messages)

            response_data = {
                'status': 'success',
                'message': 'OTP sent successfully'
            }
            return JsonResponse(response_data, status=200)  # OK status code

        else:
            response_data = {
                'status': 'error',
                'message': 'Subnet and Gateway are Missing'
            }
            return JsonResponse(response_data, status=302)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        response_data = {
            'status': 'error',
            'message': error_message
        }
        return JsonResponse(response_data, status=500)  # Internal Server Error status code


@csrf_exempt
def validate_customer_otp(request):
    mobile = request.POST.get('mobile')
    otp = request.POST.get('otp')
    if not mobile:
        response_data = {
            'status': 'error',
            'message': 'mobile field value missing'
        }
        return JsonResponse(response_data, status=400)

    if not otp:
        response_data = {
            'status': 'error',
            'message': 'otp field value missing'
        }
        return JsonResponse(response_data, status=400)

    customer = HotspotCustomer.objects.filter(mobile=mobile).first()
    if customer:
        if customer.otp_expire_time > datetime.now():
            if str(customer.otp_token) == str(otp):
                token = generate_customer_token(customer.id, otp)
                response_data = {
                    'status': 'success',
                    'message': 'OTP is Valid',
                    'login_token': token
                }
                return JsonResponse(response_data, status=200)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Invalid OTP'
                }
                return JsonResponse(response_data, status=400)

        else:
            response_data = {
                'status': 'error',
                'message': 'OTP Has Expired'
            }
            return JsonResponse(response_data, status=400)

    else:
        response_data = {
            'status': 'error',
            'message': 'Customer with this mobile number does not exist'
        }
        return JsonResponse(response_data, status=404)  # Not Found status code


def generate_customer_token(customer_id, otp):
    payload = {
        'customer_id': customer_id,
        'otp': otp
    }
    token = jwt.encode(payload, settings.SECRET_KEY)
    token_data = HotspotCustomerToken.objects.filter(token=token).first()
    if not token_data:
        token_data = HotspotCustomerToken()

    token_data.token = token
    token_data.expire_at = datetime.now() + timedelta(days=180)
    token_data.customer_id = customer_id
    token_data.status = 1
    token_data.save()

    HotspotCustomerToken.objects.exclude(token=token).filter(customer_id=customer_id).update(
        expire_at=datetime.now(), status=0)
    return token


@csrf_exempt
def token_validate(request):
    token = request.POST.get('token')
    if not token:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=302)

    token_data = HotspotCustomerToken.objects.filter(token=token).first()
    if token_data:
        current_time = datetime.now()
        if token_data.expire_at >= current_time and token_data.status != 0:
            response_data = {
                'status': 'success',
                'message': 'Token is valid'
            }
            return JsonResponse(response_data, status=200)
        else:
            response_data = {
                'status': 'error',
                'message': 'Token has expired'
            }
            return JsonResponse(response_data, status=404)
    else:
        response_data = {
            'status': 'error',
            'message': 'Invalid Token'
        }
        return JsonResponse(response_data, status=404)


@csrf_exempt
def get_phone_by_token(request):
    token = request.POST.get('token')
    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=302)
    else:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                customer_id = token_data.customer_id
                customer = HotspotCustomer.objects.get(id=customer_id)
                if customer:
                    if customer.mobile.startswith("+88"):
                        phone_number_without_prefix = customer.mobile[3:]
                        response_data = {
                            'status': 'success',
                            'phone': phone_number_without_prefix
                        }
                        return JsonResponse(response_data, status=200)
                else:
                    response_data = {
                        'status': 'error',
                        'message': 'Customer Not Found'
                    }
                    return JsonResponse(response_data, status=404)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Token has expired'
                }
                return JsonResponse(response_data, status=404)
        else:
            response_data = {
                'status': 'error',
                'message': 'Invalid Customer Token'
            }
            return JsonResponse(response_data, status=404)


@csrf_exempt
def get_customer_details_by_token(request):
    token = request.POST.get('token')
    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=302)

    else:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                customer_id = token_data.customer_id
                customer = HotspotCustomer.objects.get(id=customer_id)
                if customer:
                    if customer.mobile.startswith("+88"):
                        phone_number_without_prefix = customer.mobile[3:]
                        response_data = {
                            'status': 'success',
                            'phone': phone_number_without_prefix,
                            'validity': customer.package_expire_date
                        }
                        return JsonResponse(response_data, status=200)
                else:
                    response_data = {
                        'status': 'error',
                        'message': 'Customer Not Found'
                    }
                    return JsonResponse(response_data, status=404)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Token has expired'
                }
                return JsonResponse(response_data, status=404)
        else:
            response_data = {
                'status': 'error',
                'message': 'Invalid Token'
            }
            return JsonResponse(response_data, status=404)


def remove_active_user_from_hotspot_router(user, admin):
    if user.startswith("+88"):
        user = user[3:]
    admin_user = Users.objects.get(id=admin)
    if admin_user.user_type == 'RS-5005':
        seller = Seller.objects.filter(user_id=admin).first()
        router_list = UserHotspotRouter.objects.filter(seller_id=seller.id).first()
        if router_list:
            for data in eval(router_list.router_list):
                router = HotspotRouter.objects.get(id=int(data))
                connection = MikroTikManager(ip=router.ip_address, username=router.user_name, password=router.password,
                                             port=router.api_port)

                connect = connection.connect()
                try:
                    active_user = list(connection.connect().path('/ip/hotspot/active').select(Key('.id')).where(
                        Key('user') == str(user)))
                    if len(active_user) > 0:
                        id = active_user[0].get('.id')
                        connect.path("/ip/hotspot/active").remove(str(id))
                except Exception as e:
                    print("Can't Remove Active user")
    if admin_user.user_type == 'GA-4004':
        router_list = GeneralAdminConfig.objects.filter(admin_id=admin).first()
        if router_list:
            for data in eval(router_list.hotspot_router_list):
                router = HotspotRouter.objects.get(id=int(data))
                connection = MikroTikManager(ip=router.ip_address, username=router.user_name, password=router.password,
                                             port=router.api_port)

                connect = connection.connect()
                try:
                    active_user = list(connection.connect().path('/ip/hotspot/active').select(Key('.id')).where(
                        Key('user') == str(user)))
                    if len(active_user) > 0:
                        id = active_user[0].get('.id')
                        connect.path("/ip/hotspot/active").remove(str(id))
                except Exception as e:
                    print("Can't Remove Active user")


def create_router_user(user, admin):
    if user.startswith("+88"):
        user = user[3:]
    admin_user = Users.objects.get(id=admin)
    if admin_user.user_type == 'RS-5005':
        seller = Seller.objects.filter(user_id=admin).first()
        router_list = UserHotspotRouter.objects.filter(seller_id=seller.id).first()
        if router_list:
            for data in eval(router_list.router_list):
                router = HotspotRouter.objects.get(id=int(data))
                connection = MikroTikManager(ip=router.ip_address, username=router.user_name, password=router.password,
                                             port=router.api_port)

                connect = connection.connect()
                try:
                    user_id = connect.path("/ip/hotspot/user").add(name=user)
                    params = {'disabled': True, '.id': user_id}
                    connect.path("/ip/hotspot/user").update(**params)

                except Exception as e:
                    print("Can't add user")


def enable_router_user(user, admin):
    if user.startswith("+88"):
        user = user[3:]
    admin_user = Users.objects.get(id=admin)
    if admin_user.user_type == 'RS-5005':
        seller = Seller.objects.filter(user_id=admin).first()
        router_list = UserHotspotRouter.objects.filter(seller_id=seller.id).first()
        if router_list:
            for data in eval(router_list.router_list):
                router = HotspotRouter.objects.get(id=int(data))
                connection = MikroTikManager(ip=router.ip_address, username=router.user_name, password=router.password,
                                             port=router.api_port)
                connect = connection.connect()
                try:
                    user_data = list(connect.path("/ip/hotspot/user").select(Key('.id')).where(Key('name') == user))
                    if not len(user_data) > 0:
                        connect.path("/ip/hotspot/user").add(name=user)
                except Exception as e:
                    print("Can't update user")

    if admin_user.user_type == 'GA-4004':
        router_list = GeneralAdminConfig.objects.filter(admin_id=admin).first()
        if router_list:
            for data in eval(router_list.hotspot_router_list):
                router = HotspotRouter.objects.get(id=int(data))
                connection = MikroTikManager(ip=router.ip_address, username=router.user_name, password=router.password,
                                             port=router.api_port)
                connect = connection.connect()
                try:
                    user_data = list(connect.path("/ip/hotspot/user").select(Key('.id')).where(Key('name') == user))
                    if not len(user_data) > 0:
                        connect.path("/ip/hotspot/user").add(name=user)
                except Exception as e:
                    print("Can't update user")


def enable_ssh_router_user(user, admin):
    customer = HotspotCustomer.objects.filter(mobile=user).first()
    if user.startswith("+88"):
        user = user[3:]
    admin_user = Users.objects.get(id=admin)
    if admin_user.user_type == 'RS-5005':
        seller = Seller.objects.filter(user_id=admin).first()
        router_list = UserHotspotRouter.objects.filter(seller_id=seller.id).first()
        if router_list:
            for data in eval(router_list.router_list):
                try:
                    router = HotspotRouter.objects.get(id=int(data))
                    connection = MikroTikSSHManager.connect_router(router.ip_address, router.user_name,
                                                                   router.password,
                                                                   router.ssh_port)

                    connection.exec_command(
                        f'/ip hotspot ip-binding add comment="{user}" mac-address={customer.mac_address} type=bypassed;')

                except Exception as e:
                    print("Can't add user")

    if admin_user.user_type == 'GA-4004':
        router_list = GeneralAdminConfig.objects.filter(admin_id=admin).first()
        if router_list:
            for data in eval(router_list.hotspot_router_list):
                try:
                    router = HotspotRouter.objects.get(id=int(data))
                    connection = MikroTikSSHManager.connect_router(router.ip_address, router.user_name,
                                                                   router.password,
                                                                   router.ssh_port)
                    connection.exec_command(
                        f'/ip hotspot ip-binding add comment="{user}" mac-address={customer.mac_address} type=bypassed;')
                except Exception as e:
                    print("Can't add user")


@csrf_exempt
def check_validity(request):
    token = request.POST.get('token')
    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=401)

    else:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                customer_id = token_data.customer_id
                customer = HotspotCustomer.objects.get(id=customer_id)
                if customer:
                    if customer.package_expire_date >= current_time:
                        response_data = {
                            'status': 'success',
                            'valid': True
                        }
                        return JsonResponse(response_data, status=200)

                    else:
                        response_data = {
                            'status': 'error',
                            'message': "You haven't enough balance.."
                        }
                        return JsonResponse(response_data, status=302)

                else:
                    response_data = {
                        'status': 'error',
                        'message': 'Customer Not Found'
                    }
                    return JsonResponse(response_data, status=404)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Token has expired'
                }
                return JsonResponse(response_data, status=404)
        else:
            response_data = {
                'status': 'error',
                'message': 'Customer Invalid Token'
            }
            return JsonResponse(response_data, status=404)


@csrf_exempt
def update_mac_address(request):
    token = request.POST.get('token')
    gateway = request.POST.get('gateway')
    ip_address = request.POST.get('wifi_ip')

    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=401)

    elif ip_address is None:
        response_data = {
            'status': 'error',
            'message': 'ip_address field is required'
        }
        return JsonResponse(response_data, status=401)

    else:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        if token_data:
            current_time = datetime.now()
            if token_data.expire_at >= current_time and token_data.status != 0:
                customer_id = token_data.customer_id
                customer = HotspotCustomer.objects.get(id=customer_id)
                if customer:
                    if customer.package_expire_date >= current_time:
                        ip_address_mac = HotspotHostIpMac.objects.filter(ip_address=ip_address).first()
                        if ip_address_mac:
                            if ip_address_mac.mac_address != customer.mac_address:
                                customer.mac_address = ip_address_mac.mac_address
                                customer.save()

                        response_data = {
                            'status': 'success',
                            'valid': True
                        }
                        return JsonResponse(response_data, status=200)

                    else:
                        response_data = {
                            'status': 'error',
                            'message': "You haven't enough balance.."
                        }
                        return JsonResponse(response_data, status=302)

                else:
                    response_data = {
                        'status': 'error',
                        'message': 'Customer Not Found'
                    }
                    return JsonResponse(response_data, status=404)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Token has expired'
                }
                return JsonResponse(response_data, status=404)
        else:
            response_data = {
                'status': 'error',
                'message': 'Customer Invalid Token'
            }
            return JsonResponse(response_data, status=404)

from datetime import datetime, timedelta
from django.db import transaction
from django.http import JsonResponse

from apps.config.models import GeneralAdminConfig
from apps.hotspot_card.models import HotspotCard
from apps.hotspot_customer.api_view import enable_ssh_router_user
from apps.hotspot_customer.models import HotspotCustomerToken, HotspotCustomer
from django.views.decorators.csrf import csrf_exempt

from apps.hotspot_package.models import HotspotPackage, SellerHotspotPackage
from apps.seller.models import Seller
from apps.user.models import Users
from system.all_utils.ip_address import ip_address_check_with_subnet


@csrf_exempt
@transaction.atomic
def apply_hotspot_card(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        if token is None:
            response_data = {
                'status': 'error',
                'message': 'please provide customer token'
            }
            return JsonResponse(response_data, status=302)
        else:
            customer_token = HotspotCustomerToken.objects.filter(token=token).first()
            if customer_token is None:
                response_data = {
                    'status': 'error',
                    'message': 'Invalid Token'
                }
                return JsonResponse(response_data, status=404)
            else:
                if customer_token.status == 0 or customer_token.expire_at < datetime.now():
                    response_data = {
                        'status': 'error',
                        'message': 'This token have expired'
                    }
                    return JsonResponse(response_data, status=302)
                else:
                    customer = HotspotCustomer.objects.get(id=customer_token.customer_id)
                    card = request.POST.get('card')
                    if card is None:
                        response_data = {
                            'status': 'error',
                            'message': 'Card Number is required'
                        }
                        return JsonResponse(response_data, status=302)
                    else:
                        hot_spot = HotspotCard.objects.filter(code=card).first()
                        if hot_spot is None:
                            response_data = {
                                'status': 'error',
                                'message': 'Invalid Card Number'
                            }
                            return JsonResponse(response_data, status=302)
                        else:
                            if hot_spot.status == 0:
                                response_data = {
                                    'status': 'error',
                                    'message': 'This card have already used'
                                }
                                return JsonResponse(response_data, status=302)
                            else:
                                if hot_spot.admin_id != customer.admin_id:
                                    response_data = {
                                        'status': 'error',
                                        'message': 'This card is unauthorized fot this network..'
                                    }
                                    return JsonResponse(response_data, status=302)
                                previous_date = customer.package_expire_date
                                if customer.package_expire_date < datetime.now():
                                    customer.package_expire_date = datetime.now() + timedelta(
                                        days=hot_spot.validity)
                                else:
                                    customer.package_expire_date = customer.package_expire_date + timedelta(
                                        days=hot_spot.validity)
                                customer.save()
                                hot_spot.status = 0
                                hot_spot.customer_id = customer.id
                                hot_spot.save()


                                if previous_date < datetime.now():
                                    enable_ssh_router_user(customer.mobile, customer.admin_id)
                                response_data = {
                                    'status': 'success',
                                    'message': 'Card Applied Successfully'
                                }
                                return JsonResponse(response_data, status=200)  # OK status code


@csrf_exempt
def hotspot_package_by_token(request):
    token = request.POST.get('token')
    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=302)

    if token:
        token_data = HotspotCustomerToken.objects.filter(token=token).first()
        current_time = datetime.now()
        if token_data.expire_at >= current_time and token_data.status != 0:
            customer_id = token_data.customer_id
            customer = HotspotCustomer.objects.get(id=customer_id)
            admin_id = customer.admin_id
            if admin_id:
                user = Users.objects.get(id=admin_id)
                if user.user_type == 'RS-5005':
                    seller = Seller.objects.filter(user_id=admin_id).first()
                    package_list = SellerHotspotPackage.objects.filter(seller_id=seller.id).all()
                    data = []
                    if package_list:
                        for package in package_list:
                            package_data = {
                                'package_id': package.package_id,
                                'name': package.package.name,
                                'price': package.customer_price,
                                'days': package.package.day
                            }
                            data.append(package_data)

                    response_data = {
                        'status': 'success',
                        'message': 'Hotspot Package List',
                        'data': data
                    }
                    return JsonResponse(response_data, status=200)
                elif user.user_type == 'GA-4004':
                    package_list = HotspotPackage.objects.filter(admin_id=admin_id).all()
                    data = []
                    if package_list:
                        for package in package_list:
                            package_data = {
                                'package_id': package.id,
                                'name': package.name,
                                'price': package.price,
                                'days': package.day
                            }
                            data.append(package_data)

                    response_data = {
                        'status': 'success',
                        'message': 'Hotspot Package List',
                        'data': data
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
            'message': 'Customer Token are not valid'
        }
        return JsonResponse(response_data, status=404)

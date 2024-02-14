from datetime import datetime, timedelta
from django.db import transaction
from django.http import JsonResponse
from apps.config.models import MobileAppConfig, BkashApiConfig
from apps.hotspot_customer.models import HotspotCustomerToken, HotspotCustomer
from django.views.decorators.csrf import csrf_exempt
from apps.seller.models import Seller
from apps.user.models import Users
from system.auth.api import token_required


@csrf_exempt
@transaction.atomic
def update_apk(request):
    if request.method == 'GET':
        app_config = MobileAppConfig.objects.first()
        version_name = app_config.version_name
        apk = request.META.get('HTTP_HOST') + app_config.apk.name
        response_data = {
            'status': 'success',
            'version': version_name,
            'apk': apk
        }
        return JsonResponse(response_data, status=200)  # OK status code


@csrf_exempt
def bkash_credentials_by_token(request):
    token = request.POST.get('token')
    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=302)

    else:
        # token_data = HotspotCustomerToken.objects.filter(token=token).first()
        # if token_data:
        #     current_time = datetime.now()
        #     if token_data.expire_at >= current_time and token_data.status != 0:
        #         customer_id = token_data.customer_id
        #         customer = HotspotCustomer.objects.get(id=customer_id)
        #         if customer:
        #             admin_id = None
        #             user = Users.objects.get(id=customer.admin_id)
        #             if user.user_type == 'RS-5005':
        #                 admin_id = Seller.objects.filter(user_id=user.id).first().admin_id
        #             elif user.user_type == 'GA-4004':
        #                 admin_id = user.id
        #             if admin_id:
        #                 config = BkashApiConfig.objects.filter(admin_id=admin_id).first()
        #
        #                 response_data = {
        #                     'status': 'success',
        #                     'admin_id': str(admin_id),
        #                     'app_key': str(config.app_key) if config.app_key else '',
        #                     'secret_key': str(config.secret_key) if config.secret_key else '',
        #                     'user_name': str(config.user_name) if config.user_name else '',
        #                     'password': str(config.password) if config.password else '',
        #                     'sandbox_status': str(config.sandbox_status)
        #                 }
        #                 return JsonResponse(response_data, status=200)
        #             else:
        #                 response_data = {
        #                     'status': 'error',
        #                     'message': 'Admin have no bkash'
        #                 }
        #                 return JsonResponse(response_data, status=404)
        #
        #         else:
        #             response_data = {
        #                 'status': 'error',
        #                 'message': 'Customer Not Found'
        #             }
        #             return JsonResponse(response_data, status=404)
        #     else:
        #         response_data = {
        #             'status': 'error',
        #             'message': 'Token has expired'
        #         }
        #         return JsonResponse(response_data, status=404)
        # else:
        response_data = {
            'status': 'error',
            'message': 'Customer Invalid Token'
        }
        return JsonResponse(response_data, status=404)


@csrf_exempt
def important_notice(request):
    token = request.POST.get('token')
    if token is None:
        response_data = {
            'status': 'error',
            'message': 'Token field is required'
        }
        return JsonResponse(response_data, status=302)

    else:
        response_data = {
            'status': 'success',
            'active': '1',
            'message': '     ***বিকাশ এ হটস্পট কিনতে সমস্যা হলে তারা নতুন করে সফটওয়্যার ডাউনলোড করুন***       '
        }
        return JsonResponse(response_data, status=200)

    # token_data = HotspotCustomerToken.objects.filter(token=token).first()
    # if token_data:
    #     current_time = datetime.now()
    #     if token_data.expire_at >= current_time and token_data.status != 0:
    #         customer_id = token_data.customer_id
    #         customer = HotspotCustomer.objects.get(id=customer_id)
    #         if customer:
    #             admin_id = None
    #             user = Users.objects.get(id=customer.admin_id)
    #             if user.user_type == 'RS-5005':
    #                 admin_id = Seller.objects.filter(user_id=user.id).first().admin_id
    #             elif user.user_type == 'GA-4004':
    #                 admin_id = user.id
    #             if admin_id:
    #                 config = BkashApiConfig.objects.filter(admin_id=admin_id).first()
    #
    #                 response_data = {
    #                     'status': 'success',
    #                     'admin_id': str(admin_id),
    #                     'app_key': str(config.app_key) if config.app_key else '',
    #                     'secret_key': str(config.secret_key) if config.secret_key else '',
    #                     'user_name': str(config.user_name) if config.user_name else '',
    #                     'password': str(config.password) if config.password else '',
    #                     'sandbox_status': str(config.sandbox_status)
    #                 }
    #                 return JsonResponse(response_data, status=200)
    #             else:
    #                 response_data = {
    #                     'status': 'error',
    #                     'message': 'Admin have no bkash'
    #                 }
    #                 return JsonResponse(response_data, status=404)
    #
    #         else:
    #             response_data = {
    #                 'status': 'error',
    #                 'message': 'Customer Not Found'
    #             }
    #             return JsonResponse(response_data, status=404)
    #     else:
    #         response_data = {
    #             'status': 'error',
    #             'message': 'Token has expired'
    #         }
    #         return JsonResponse(response_data, status=404)
    # else:
    response_data = {
        'status': 'error',
        'message': 'Customer Invalid Token'
    }
    return JsonResponse(response_data, status=404)

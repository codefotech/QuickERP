import json
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.hotspot_customer.api_view import  enable_ssh_router_user
from apps.hotspot_customer.models import HotspotCustomerToken, HotspotCustomer
from apps.hotspot_package.models import HotspotPackage, SellerHotspotPackage
from apps.payment.models import PackagePurchaseHistory
from apps.seller.models import Seller
from apps.user.models import Users
from system.auth.api import token_required
from django.db import transaction


@csrf_exempt
@transaction.atomic
def purchase_package(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        package_id = request.POST.get('package_id')
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
                    customer = HotspotCustomer.objects.filter(id=customer_id).first()
                    if customer:
                        if package_id:
                            package = HotspotPackage.objects.filter(id=package_id).first()
                            if package:
                                if (request.POST.get('statusCode') == '0000' or
                                        request.POST.get('statusMessage') == "Successful" or
                                        request.POST.get('transactionStatus') == 'Completed'):
                                    previous_date = customer.package_expire_date
                                    if customer.package_expire_date < datetime.now():
                                        customer.package_expire_date = datetime.now() + timedelta(
                                            days=int(package.day))
                                    else:
                                        customer.package_expire_date = customer.package_expire_date + timedelta(
                                            days=int(package.day))
                                    customer.save()

                                    admin_id = customer.admin_id
                                    user = Users.objects.filter(id=admin_id).first()
                                    if user:
                                        if user.user_type == 'RS-5005':
                                            seller = Seller.objects.filter(user_id=user.id).first()
                                            seller_package = SellerHotspotPackage.objects.filter(package_id=package_id,
                                                                                                 seller_id=seller.id).first()

                                            seller_new_balance = float(seller_package.customer_price) - float(
                                                seller_package.price)
                                            user.wallet_balance = float(user.wallet_balance) + float(seller_new_balance)
                                            user.save()

                                    data_dict = {
                                        "statusCode": request.POST.get('statusCode') if request.POST.get(
                                            'statusCode') else '',
                                        "statusMessage": request.POST.get('statusMessage')
                                        if request.POST.get('statusMessage') else '',
                                        "paymentID": request.POST.get('paymentID') if request.POST.get(
                                            'paymentID') else '',
                                        "payerReference": request.POST.get('payerReference')
                                        if request.POST.get('payerReference') else '',
                                        "customerMsisdn": request.POST.get('customerMsisdn')
                                        if request.POST.get('customerMsisdn') else '',
                                        "trxID": request.POST.get('trxID') if request.POST.get('trxID') else '',
                                        "amount": request.POST.get('amount') if request.POST.get('amount') else '',
                                        "transactionStatus": request.POST.get('transactionStatus') if request.POST.get(
                                            'transactionStatus') else '',
                                        "paymentExecuteTime": request.POST.get(
                                            'paymentExecuteTime') if request.POST.get('paymentExecuteTime') else '',
                                        "currency": request.POST.get('currency') if request.POST.get(
                                            'currency') else '',
                                        "intent": request.POST.get('intent') if request.POST.get('intent') else '',
                                        "merchantInvoiceNumber": request.POST.get(
                                            'merchantInvoiceNumber') if request.POST.get(
                                            'merchantInvoiceNumber') else ''
                                    }
                                    history = PackagePurchaseHistory()
                                    history.package_id = package.id
                                    history.admin_id = customer.admin_id
                                    history.customer_id = customer.id
                                    history.response = json.dumps(data_dict)
                                    history.save()

                                    if previous_date < datetime.now():
                                        enable_ssh_router_user(customer.mobile, customer.admin_id)

                                    response_data = {
                                        'status': 'success',
                                        'message': 'Package Successfully Purchased.'
                                    }
                                    return JsonResponse(response_data, status=200)
                            else:
                                response_data = {
                                    'status': 'error',
                                    'message': 'Package Is Not Found'
                                }
                                return JsonResponse(response_data, status=404)
                        else:
                            response_data = {
                                'status': 'error',
                                'message': 'Package Field Required'
                            }
                            return JsonResponse(response_data, status=404)
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

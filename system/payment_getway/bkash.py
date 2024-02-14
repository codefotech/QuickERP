import json
import random
from datetime import datetime, timedelta

from django.http import HttpResponse

from apps.config.models import BkashApiConfig
from apps.hotspot_customer.api_view import enable_ssh_router_user
from apps.hotspot_customer.models import HotspotCustomer
from apps.hotspot_package.models import HotspotPackage, SellerHotspotPackage
from apps.payment.balance import final_add_balance
from apps.payment.models import BkashPackagePurchaseRequest
from apps.seller.models import Seller
from apps.user.models import Users
from system.enums.enum import PaymentTypeEnum
from django.shortcuts import render, redirect
import requests
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from system.config import _thread_local
from django.db import transaction


class BkashPayment:
    def __init__(self):

        self.headers = {}

    def pay(self, request):
        amount = 0
        if 'payment_type' in request.session:
            payment_type = request.session.get('payment_type')
            payment_data = request.session.get('payment_data')

            if payment_type == 'wallet_payment':
                amount = float(payment_data['amount']) if payment_data['amount'] else 0.00
            # elif payment_type == 'seller_package_payment':
            #     # Replace SellerPackage with your Django model and adjust the logic accordingly
            #     seller_package = SellerPackage.objects.get(pk=payment_data['seller_package_id'])
            #     amount = round(seller_package.amount)
            elif (payment_type == PaymentTypeEnum.add_balance or payment_type == 'store_balance'
                  or payment_type == 'vlan_balance' or payment_type == 'pay_bill_online'
                  or payment_type == 'buy_hotspot_online'):
                amount = float(payment_data['amount']) if payment_data['amount'] else 0.00

        request_data = {
            'app_key': get_config().app_key,
            'app_secret': get_config().secret_key
        }

        headers = {
            'Content-Type': 'application/json',
            'username': get_config().user_name,
            'password': get_config().password
        }

        response = requests.post(get_base_url() + 'checkout/token/grant',
                                 json=request_data, headers=headers)

        token = response.json().get('id_token')

        request.session['bkash_token'] = token
        request.session['payment_amount'] = amount

        return render(request, 'frontend/bkash/index.html', context={'amount': amount})

    @csrf_exempt
    def checkout(self, request):
        auth = request.session.get('bkash_token')
        request_body = {
            'mode': '0011',
            'amount': request.session.get('payment_amount'),
            'currency': 'BDT',
            'intent': 'sale',
            "callbackURL": request.build_absolute_uri(reverse('bkash_success')),  # Replace with your callback URL
            "payerReference": request.user.user_mobile,
            'merchantInvoiceNumber': f"Inv-{random.randint(1, 200000000)}"
        }

        checkout_url = get_base_url() + 'checkout/create'
        request_body_json = json.dumps(request_body)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth,
            'X-APP-Key': get_config().app_key
        }

        try:
            response = requests.post(checkout_url, headers=headers, data=request_body_json)
            if response.status_code == 200:
                print(response.json())
                return HttpResponse(response)
            else:
                print("Error:", response.text)
                return HttpResponse(response.text)

        except requests.exceptions.RequestException as e:
            print("Error:", e)

    @csrf_exempt
    def execute(self, request):
        payment_id = request.session.get('payment_id')  # Replace with your payment ID
        auth = request.session.get('bkash_token')  # Replace with your bKash token
        execute_url = get_base_url() + 'checkout/execute'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth,
            'X-APP-Key': get_config().app_key  # Replace with your bKash checkout app key
        }
        post_token = {
            'paymentID': payment_id
        }
        post_token_json = json.dumps(post_token)
        try:
            response = requests.post(execute_url, headers=headers, data=post_token_json)
            if response.status_code == 200:
                result_data = response.json()
                request.session['payment_details'] = result_data

                return redirect("bkash_success_two")
            else:
                print("Error:", response.text)
        except requests.exceptions.RequestException as e:
            print("Error:", e)

    def success(self, request):
        if request.GET.get('status') == 'success':
            request.session['payment_id'] = request.GET.get('paymentID')
            return redirect('bkash_execute')

    def success_two(self, request):
        if request.session['payment_details'].get('statusCode') == '2062' or request.session['payment_details'].get(
                'statusCode') == '0000' or request.session['payment_details'].get('statusMessage') == 'Successful':
            payment_type = request.session.get('payment_type')
            payment_details = request.session.get('payment_details')
            payment_data = request.session.get('payment_data')
            if payment_type == PaymentTypeEnum.add_balance:
                return final_add_balance(request, payment_data, payment_details)

        else:
            return HttpResponse('Please try after few minutes later ..........')


class HotspotPackageBkashPayment:
    def __init__(self):
        self.headers = {}

    def payment_checkout(self, request):
        amount = request.POST.get('amount')
        package_id = request.POST.get('package_id')
        customer_mobile = request.POST.get('customer_mobile')
        customer_id = request.POST.get('customer_id')
        admin_id = request.POST.get('admin_id')
        config = BkashApiConfig.objects.filter(admin_id=admin_id).first()
        base_url = "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/"
        if config:
            if config.sandbox_status:
                base_url = "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/"
            else:
                base_url = "https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/"
            request_data = {
                'app_key': config.app_key,
                'app_secret': config.secret_key
            }

            headers = {
                'Content-Type': 'application/json',
                'username': config.user_name,
                'password': config.password
            }

            response = requests.post(base_url + 'checkout/token/grant',
                                     json=request_data, headers=headers)
            if response:
                token = response.json().get('id_token')
                request_body = {
                    'mode': '0011',
                    'amount': amount,
                    'currency': 'BDT',
                    'intent': 'sale',
                    "callbackURL": request.build_absolute_uri(reverse('bkash_payment_success')),
                    "payerReference": customer_mobile,
                    'merchantInvoiceNumber': f"Inv-{random.randint(1, 200000000)}"
                }

                checkout_url = base_url + 'checkout/create'
                request_body_json = json.dumps(request_body)

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': token,
                    'X-APP-Key': config.app_key
                }

                try:
                    response = requests.post(checkout_url, headers=headers, data=request_body_json)
                    if response.status_code == 200:
                        bkash_purchase_request = BkashPackagePurchaseRequest()
                        bkash_purchase_request.package_id = package_id if package_id else ''
                        bkash_purchase_request.payment_id = response.json().get('paymentID')
                        bkash_purchase_request.invoice_no = response.json().get('merchantInvoiceNumber')
                        bkash_purchase_request.customer_id = customer_id
                        bkash_purchase_request.amount = float(amount)
                        bkash_purchase_request.config_id = config.id
                        bkash_purchase_request.save()
                        print(response.json())
                        return HttpResponse(response)
                    else:
                        print("Error:", response.text)
                        return HttpResponse(response.text)

                except requests.exceptions.RequestException as e:
                    print("Error:", e)
        else:
            return HttpResponse('Unknown Request')

    @transaction.atomic
    def bkash_payment_success(self, request, **kwargs):
        if request.GET.get('status') == 'success':
            payment_request = BkashPackagePurchaseRequest.objects.filter(
                payment_id=request.GET.get('paymentID')).first()
            if payment_request:
                config = BkashApiConfig.objects.filter(id=payment_request.config_id).first()
                if config.sandbox_status:
                    base_url = "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/"
                else:
                    base_url = "https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/"

                request_data = {
                    'app_key': config.app_key,
                    'app_secret': config.secret_key
                }

                headers = {
                    'Content-Type': 'application/json',
                    'username': config.user_name,
                    'password': config.password
                }

                response = requests.post(base_url + 'checkout/token/grant',
                                         json=request_data, headers=headers)

                execute_url = base_url + 'checkout/execute'
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': response.json().get('id_token'),
                    'X-APP-Key': config.app_key  # Replace with your bKash checkout app key
                }
                post_token = {
                    'paymentID': payment_request.payment_id
                }
                post_token_json = json.dumps(post_token)
                try:
                    response = requests.post(execute_url, headers=headers, data=post_token_json)
                    if json.loads(response.text).get('statusCode') == '2023':
                        message = 'Insufficient Balance!!!!!!'
                        return render(request, 'frontend/bkash/success.html', context={'message': message})

                    if (response.status_code == 200 and json.loads(response.text).get(
                            'statusCode') != '2023' and json.loads(response.text).get('statusCode') == '0000' or
                            json.loads(response.text).get('statusCode') == '2062'):
                        # result_data = response.json()
                        payment_request.status = 1
                        payment_request.transaction_id = json.loads(response.text).get('trxID')
                        payment_request.save()

                        customer = HotspotCustomer.objects.filter(id=payment_request.customer_id).first()
                        hotspot_package = HotspotPackage.objects.filter(id=payment_request.package_id).first()
                        previous_date = customer.package_expire_date
                        if customer.package_expire_date < datetime.now():
                            customer.package_expire_date = datetime.now() + timedelta(
                                days=int(hotspot_package.day))
                        else:
                            customer.package_expire_date = customer.package_expire_date + timedelta(
                                days=int(hotspot_package.day))

                        if previous_date < datetime.now():
                            enable_ssh_router_user(customer.mobile, customer.admin_id)
                        customer.save()

                        user = Users.objects.filter(id=customer.admin_id).first()
                        if user:
                            if user.user_type == 'RS-5005':
                                seller = Seller.objects.filter(user_id=user.id).first()
                                seller_package = SellerHotspotPackage.objects.filter(
                                    package_id=payment_request.package_id,
                                    seller_id=seller.id).first()

                                seller_new_balance = float(seller_package.customer_price) - float(
                                    seller_package.price)
                                user.wallet_balance = float(user.wallet_balance) + float(seller_new_balance)
                                user.save()
                        message = json.loads(response.text).get('statusMessage')
                        return render(request, 'frontend/bkash/success.html', context={'message': message})
                    else:
                        message = json.loads(response.text).get('statusMessage')
                        return render(request, 'frontend/bkash/success.html', context={'message': message})
                except requests.exceptions.RequestException as e:
                    print("Error:", e)

        else:
            message = 'Payment Not Successfull'
            return render(request, 'frontend/bkash/success.html', context={'message': message})


def get_base_url():
    admin_id = None
    if _thread_local.user.user_type == 'SA-2002' or _thread_local.user.user_type == 'GA-4004' or _thread_local.user.user_type == 'SUA-3003':
        admin_id = _thread_local.user.id
    elif _thread_local.user.user_type == 'G-1001':
        admin_id = _thread_local.user.admin
    elif _thread_local.user.user_type == 'RS-5005':
        seller = Seller.objects.filter(user_id=_thread_local.user.id).first()
        admin_id = seller.admin_id
    elif _thread_local.user.user_type == 'SR-6006':
        reseller = Seller.objects.filter(user_id=_thread_local.user.id).first()
        seller = Seller.objects.filter(user_id=reseller.admin_id).first()
        admin_id = seller.admin_id

    config = BkashApiConfig.objects.filter(admin_id=admin_id).first()
    if not config:
        base_url = "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/"
    else:
        if config.sandbox_status:
            base_url = "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/"
        else:
            base_url = "https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/"

    return base_url


def get_config():
    admin_id = None
    if _thread_local.user.user_type == 'SA-2002' or _thread_local.user.user_type == 'GA-4004' or _thread_local.user.user_type == 'SUA-3003':
        admin_id = _thread_local.user.id
    elif _thread_local.user.user_type == 'G-1001':
        admin_id = _thread_local.user.admin
    elif _thread_local.user.user_type == 'RS-5005':
        seller = Seller.objects.filter(user_id=_thread_local.user.id).first()
        admin_id = seller.admin_id
    elif _thread_local.user.user_type == 'SR-6006':
        reseller = Seller.objects.filter(user_id=_thread_local.user.id).first()
        seller = Seller.objects.filter(user_id=reseller.admin_id).first()
        admin_id = seller.admin_id

    config = BkashApiConfig.objects.filter(admin_id=admin_id).first()
    if not config:
        return None
    else:
        return config

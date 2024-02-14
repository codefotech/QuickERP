from django.http import HttpResponse
from django.shortcuts import render
from apps.hotspot_customer.models import HotspotCustomerToken, HotspotCustomer
from apps.hotspot_package.models import HotspotPackage, SellerHotspotPackage
from apps.seller.models import Seller
from apps.user.models import Users
from system.enums.enum import PaymentMethodEnum, PaymentTypeEnum
from system.payment_getway.bkash import BkashPayment


# Create your views here.

def add_balance(request):
    data = {
        'amount': request.POST.get('amount'),
        'payment_method': PaymentMethodEnum.__getattr__(request.POST.get('payment_method')) if request.POST.get(
            'payment_method') else ''
    }

    request.session['payment_type'] = PaymentTypeEnum.add_balance
    request.session['payment_data'] = data

    return BkashPayment().pay(request)


def purchase_hotspot_package(request):
    context = {}
    if request.GET.get('package_id') and request.GET.get('token'):
        package_id = request.GET.get('package_id')
        context['package_id'] = package_id
        token = request.GET.get('token')
        context['amount'] = 0
        customer_id = HotspotCustomerToken.objects.filter(token=token).first().customer_id
        customer = HotspotCustomer.objects.filter(id=customer_id).first()
        context['customer_mobile'] = customer.mobile
        context['customer_id'] = customer_id
        amount = 0
        user = Users.objects.filter(id=customer.admin_id).first()
        if user.user_type == 'GA-4004':
            amount = HotspotPackage.objects.filter(id=package_id).first().price
            context['amount'] = amount
            context['admin_id'] = user.id
        if user.user_type == 'RS-5005':
            seller = Seller.objects.filter(user_id=user.id).first()
            seller_package = SellerHotspotPackage.objects.filter(package_id=package_id,
                                                                 seller_id=seller.id).first()
            if seller_package:
                amount = seller_package.customer_price
            context['amount'] = amount
            context['admin_id'] = seller.admin_id
    else:
        return HttpResponse('You have not provide token and package_id')
    return render(request, 'frontend/bkash/purchase_package_with_bkash.html', context=context)

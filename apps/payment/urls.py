from django.urls import path
from apps.payment.views import *
from system.payment_getway.bkash import BkashPayment, HotspotPackageBkashPayment

urlpatterns = [
    path('add_balance', add_balance, name='add_wallet_balance'),
    path('purchase_hotspot_package', purchase_hotspot_package, name='purchase_hotspot_package'),

    # Bkash
    path('bkash/bkash_checkout', BkashPayment().checkout, name='bkash_checkout'),
    path('bkash/success', BkashPayment().success, name='bkash_success'),
    path('bkash/execute', BkashPayment().execute, name='bkash_execute'),
    path('bkash/bkash_success_two', BkashPayment().success_two, name='bkash_success_two'),

    # Bkash PackagePurchase
    path('bkash/hotspot_package_bkash_payment_checkout', HotspotPackageBkashPayment().payment_checkout,
         name='hotspot_package_bkash_payment_checkout'),
    path('bkash/bkash_payment_success', HotspotPackageBkashPayment().bkash_payment_success,
         name='bkash_payment_success')

]

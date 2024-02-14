from django.urls import path, include
from apps.payment.api_view import *
from system.payment_getway.bkash import HotspotPackageBkashPayment
from apps.payment.views import *

urlpatterns = [
    path('api/v1/customer/purchase_package', purchase_package, name='purchase_package'),
    path('api/v1/customer/hotspot_package_purchase', purchase_hotspot_package,
         name='hotspot_package_purchase'),
]

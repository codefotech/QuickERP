from django.urls import path, include
from apps.hotspot_package.api_view import *

urlpatterns = [
    path('api/v1/hotspot_package/hotspot_package_by_token', hotspot_package_by_token, name='hotspot_package_by_token'),

]

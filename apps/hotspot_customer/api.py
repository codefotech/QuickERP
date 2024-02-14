from django.urls import path, include
from apps.hotspot_customer.api_view import *

urlpatterns = [
    path('api/v1/customer/customer_create_or_otp_send', customer_create_or_otp_send, name='customer_create_or_otp_send'),
    path('api/v1/customer/validate_customer_otp', validate_customer_otp, name='validate_customer_otp'),
    path('api/v1/customer/validate_token', token_validate, name='validate_customer_token'),
    path('api/v1/customer/get_phone_by_token', get_phone_by_token, name='get_phone_by_token'),
    path('api/v1/customer/check_validity', check_validity, name='check_validity'),
    path('api/v1/customer/update_mac_address', update_mac_address, name='update_mac_address'),
    path('api/v1/customer/get_customer_details_by_token', get_customer_details_by_token, name='get_customer_details_by_token'),


]

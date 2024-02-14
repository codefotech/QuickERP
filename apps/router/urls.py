from django.urls import path
from apps.router.views import *

urlpatterns = [
    path('', index, name='router_list'),
    path('router_data', data_json_response, name='router_data'),
    path('add/', add, name='router_add'),
    path('edit/<int:id>', edit, name='router_edit'),
    path('router_list', router_realtime_data, name='list_data_router'),
    path('get_package_info_by_router', get_package_info_by_router, name='get_package_info_by_router'),
    path('router_status', get_router_active_status, name='get_router_active_status'),
    path('router_import', router_import, name='router_import'),
    # path('hotspot_profile', hotspot_profile, name='hotspot_profile'),
    # path('activation', activation, name='activation'),
    # path('customer_list', customer_list, name='customer_list'),
    # path('all_seller', all_seller, name='all_seller'),
    # path('assign_profiles', assign_profiles, name='assign_profiles'),
    # path('assign_vlans', assign_vlans, name='assign_vlans'),
    # path('payouts', payouts, name='payouts'),
    # path('payouts_requests', payouts_requests, name='payouts_requests'),
    # path('seller_verification_form', seller_verification_form, name='seller_verification_form'),
    # path('send_message_to_socket', send_message_to_socket, name='send_message_to_socket')
]
from django.urls import path
from apps.hotspot_customer.views import *

urlpatterns = [
    path('', index, name='hotspot_customer_list'),
    path('list', data_json_response, name='hotspot_customer_data'),
    path('add/', add, name='hotspot_customer_add'),
    path('edit/<int:id>', edit, name='hotspot_customer_edit'),
    path('add_validity/', hotspot_customer_validity_add, name='hotspot_customer_validity_add'),
    path('hotspot_customer_update_ip/', hotspot_customer_update_ip, name='hotspot_customer_update_ip'),
    path('get_hotspot_customer_active_status/', get_hotspot_customer_active_status,
         name='get_hotspot_customer_active_status'),
]

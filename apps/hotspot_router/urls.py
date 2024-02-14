from django.urls import path
from apps.hotspot_router.views import *

urlpatterns = [
    path('', index, name='hotspot_router_list'),
    path('data', data_json_response, name='hotspot_router_data'),
    path('add/', add, name='hotspot_router_add'),
    path('edit/<int:id>/', edit, name='hotspot_router_edit'),
    path('assign_hotspot_router_list', assign_hotspot_router_list, name='assign_hotspot_router_list'),
    path('assign_hotspot_router', assign_hotspot_router, name='assign_hotspot_router'),
    path('assign_hotspot_router/edit/<int:id>', edit_assign_hotspot_router, name='edit_assign_hotspot_router'),
    path('hotspot_router_status', get_hotspot_router_active_status, name='get_hotspot_router_active_status'),

]
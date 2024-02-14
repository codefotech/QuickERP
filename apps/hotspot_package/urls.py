from django.urls import path
from apps.hotspot_package.views import *

urlpatterns = [
    path('', index, name='hotspot_package_list'),
    path('data', data_json_response, name='hotspot_package_data'),
    path('add/', add, name='hotspot_package_add'),
    path('edit/<int:id>', edit, name='hotspot_package_edit'),
    path('assign_hotspot_package', assign_hotspot_package, name='assign_hotspot_package'),
    path('assign_seller_list', assign_seller_list, name='assign_hotspot_seller_list'),
    path('assign/<int:id>', assign_seller_hotspot_package, name='assign_seller_hotspot_package'),
    path('assign_new_hotspot_package/<int:id>', assign_new_hotspot_package, name='assign_new_hotspot_package'),
    path('assign_hotspot_package/edit/<int:id>', edit_assign_hotspot_package, name='edit_assign_hotspot_package'),
    path('seller_own_hotspot_package_list', seller_own_hotspot_package, name='seller_own_hotspot_package_list'),
    path('seller_own_hotspot_package_price_update/', seller_own_package_edit_view, name='seller_own_hotspot_package_price_update'),

]
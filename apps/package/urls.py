from django.urls import path
from apps.package.views import *

urlpatterns = [
    path('', index, name='package_list'),
    path('data', data_json_response, name='package_data'),
    path('add/', add, name='package_add'),
    path('edit/<int:id>', edit, name='package_edit'),
    path('assign_package', assign_package, name='assign_package'),
    path('assign_seller_list', assign_seller_list, name='assign_seller_list'),
    path('assign/<int:id>', assign_seller_package, name='assign_seller_package'),
    path('reseller_assign/<int:id>', assign_reseller_package, name='assign_reseller_package'),

    path('assign_new_package/<int:id>', assign_new_package, name='assign_new_package'),
    path('assign_package/edit/<int:id>', edit_assign_package, name='edit_assign_package'),
    path('seller_own_package_list', seller_own_package_list, name='seller_own_package_list')
]
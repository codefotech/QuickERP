from django.urls import path
from apps.seller.views import *

urlpatterns = [
    path('', index, name='seller_list'),
    path('list', data_json_response, name='seller_data'),
    path('add/', add, name='seller_add'),
    path('edit/<int:id>', edit, name='seller_edit'),
    path('seller_package_data/', seller_package_data, name='seller_package_data'),
]

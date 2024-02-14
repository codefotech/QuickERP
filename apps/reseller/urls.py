from django.urls import path
from apps.reseller.views import *

urlpatterns = [
    path('', index, name='reseller_list'),
    path('list', data_json_response, name='reseller_data'),
    path('add/', add, name='reseller_add'),
    path('edit/<int:id>', edit, name='reseller_edit'),
]

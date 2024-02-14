from django.urls import path
from apps.iptv.views import *

urlpatterns = [
    path('', index, name='iptv_list'),
    path('iptv_data', data_json_response, name='iptv_data'),
    path('add/', add, name='iptv_add'),
    path('edit/<int:id>', edit, name='iptv_edit')
]
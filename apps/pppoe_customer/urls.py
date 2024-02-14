from django.urls import path
from apps.pppoe_customer.views import *

urlpatterns = [
    path('', index, name='pppoe_customer_list'),
    path('add/', add, name='pppoe_customer_add'),
    path('edit/<int:id>', edit, name='pppoe_customer_edit'),
]
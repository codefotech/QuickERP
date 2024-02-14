from django.urls import path
from .views import *

urlpatterns = [
    path('income', income, name='income_report'),
    path('expense', expense, name='expense_report'),
    path('bkash_purchase_history/', bkash_purchase_history, name='bkash_purchase_history'),
]

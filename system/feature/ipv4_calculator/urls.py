from django.urls import path, include
from system.feature.ipv4_calculator.views import ipv4_calculator

urlpatterns = [
    path('', ipv4_calculator, name='ipv4_calculator')
]

from django.urls import path, include
from .views import dashboard
from apps.user.views import login

urlpatterns = [
    path('', dashboard, name='dashboard'),
]
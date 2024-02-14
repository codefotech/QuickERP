from django.urls import path
from . import views

urlpatterns = [
    # Your existing URL patterns
    path('save_sms_gateway_config/', views.save_sms_gateway_config, name='save_sms_gateway_config'),
]
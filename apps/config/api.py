from django.urls import path, include
from apps.config.api_view import *

urlpatterns = [
    path('api/v1/config/apk_update', update_apk, name='update_apk'),
    path('api/v1/config/bkash_credentials_by_token', bkash_credentials_by_token, name='bkash_credentials_by_token'),
    path('api/v1/config/important_notice', important_notice, name='important_notice'),

]

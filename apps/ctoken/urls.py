from django.urls import path
from apps.ctoken.views import *

urlpatterns = [
    path('get_token', generate_token_api, name='generate_token_api'),
]

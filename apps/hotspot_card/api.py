from django.urls import path, include
from apps.hotspot_card.api_view import *

urlpatterns = [
    path('api/v1/hotspot_card/apply', apply_hotspot_card, name='apply_hotspot_card'),

]

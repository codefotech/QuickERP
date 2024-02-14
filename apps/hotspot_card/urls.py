from django.urls import path
from apps.hotspot_card.views import *

urlpatterns = [
    path('', index, name='hotspot_card_list'),
    path('list', data, name='hotspot_card_data'),
    path('generate_card/', generate_card, name='hotspot_card_generate_card'),
    path('generate_pdf/', generate_pdf, name='generate_pdf')
    # path('edit/<int:id>', edit, name='hotspot_card_edit'),
    # path('add_validity/', hotspot_card_validity_add, name='hotspot_card_validity_add'),
]

from django.urls import path, include
from apps.hotspot_customer.api import urlpatterns as hotspot_customer_api
from apps.hotspot_card.api import urlpatterns as hotspot_card_api
from apps.config.api import urlpatterns as config_api
from apps.hotspot_package.api import urlpatterns as hotspot_package_api
from apps.payment.api import urlpatterns as payment_api
urlpatterns = hotspot_customer_api + hotspot_card_api + config_api + hotspot_package_api + payment_api

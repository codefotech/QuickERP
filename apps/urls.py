from django.urls import path, include
from apps.home.views import home, live
from apps.hotspot_customer.views import hotspot_login, valid_otp, hotspot_dashboard, hotspot_customer_mac_update
from apps.user.views import login, logout_view
from apps.api import urlpatterns as api_urlpatterns
from system.urls import urlpatterns as system_urls
urlpatterns = [
                  path('', home, name='home'),
                  path('login/', login, name='login'),
                  path('logout/', logout_view, name='logout'),
                  path('live/', live, name='live'),
                  path('dashboard/', include('apps.dashboard.urls')),
                  path('user/', include('apps.user.urls')),
                  path('routers/', include('apps.router.urls')),
                  path('hotspot_router/', include('apps.hotspot_router.urls')),
                  path('iptv/', include('apps.iptv.urls')),
                  path('package/', include('apps.package.urls')),
                  path('hotspot_package/', include('apps.hotspot_package.urls')),
                  path('hotspot_card/', include('apps.hotspot_card.urls')),
                  path('sellers/', include('apps.seller.urls')),
                  path('resellers/', include('apps.reseller.urls')),
                  path('config/', include('apps.config.urls')),
                  path('sms/', include('apps.sms.urls')),
                  path('pppoe_customer/', include('apps.pppoe_customer.urls')),
                  path('payment/', include('apps.payment.urls')),
                  path('hotspot_customers/', include('apps.hotspot_customer.urls')),
                  path('api/v1/token/', include('apps.ctoken.urls')),
                  path('reports/', include('apps.reports.urls')),
                  path('hotspot_user_login', hotspot_login, name='hotspot_login'),
                  path('hotspot_user_otp_validate/<str:mobile>', valid_otp, name='hotspot_user_otp_validate'),
                  path('hotspot_dashboard', hotspot_dashboard, name='hotspot_dashboard'),
                  path('hotspot_customer_mac_update/', hotspot_customer_mac_update, name='hotspot_customer_mac_update')
              ] + api_urlpatterns + system_urls

from django.urls import path

from apps.config.payment_getway.views import bkash_config
from apps.config.general.views import *
from apps.config.views import *

urlpatterns = [
    path('otp-configuration', otp_configuration, name='otp_configuration'),
    path('otp-configuration_update', otp_configuration_update, name='otp_configuration_update'),
    path('sms-template', sms_template, name='sms_template'),
    path('set-otp-credentials', set_otp_credentials, name='set_otp_credentials'),

    # Payment Gateway Url
    path('bkash_config', bkash_config, name='bkash_config'),

    # General Config
    path('app_settings', app_settings, name='app_settings'),
    path('admin_general_settings', admin_general_settings ,name='admin_general_settings'),

    path('cron/ssh_router_user_add_remove_cron', ssh_router_user_add_remove_cron, name='ssh_router_user_add_remove'),
    path('cron/update_hotspot_customer_mac_cron', update_hotspot_customer_mac_cron, name='update_hotspot_customer_mac_cron'),
    path('cron/update_hotspot_mac_ip_cron', update_hotspot_mac_ip_cron, name='update_hotspot_customer_mac_cron'),

]

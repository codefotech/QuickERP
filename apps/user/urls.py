from django.urls import path
from apps.user.views import *

urlpatterns = [
    path('', index, name='user_list'),
    path('add', add, name='user_add'),
    path('edit/<int:id>', edit, name='user_edit'),
    path('user_data', data_json_response, name='user_data'),
    path('user_type_data', user_type_data_json_response, name='user_type_data'),
    path('sendotp/', sendotp, name='sendotp'),
    path('forgot_pass/', forgot_pass, name='forgot_pass'),
    path('submit_otp/', submit_otp, name='submit_otp'),
    path('reset_password/', reset_password, name='reset_password'),
    path('verify_email/', verify_email, name='verify_email'),
    path('permission/', user_permission, name='user_permission'),
    path('assign_permission/<int:id>', assign_permission, name='assign_permission')



    # path('countries', countries, name='countries'),
    # path('states', states, name='states'),
    # path('cities', cities, name='cities'),
    # path('zones', zones, name='zones'),
    # path('wallet_recharge_history', wallet_recharge_history, name='wallet_recharge_history'),
    # path('ticket', ticket, name='ticket'),
    # path('header', header, name='header'),
    # path('footer', footer, name='footer'),
    # path('pages', pages, name='pages'),
    # path('appearance', appearance, name='appearance'),
    # path('general_settings', general_settings, name='general_settings'),
    # path('languages', languages, name='languages'),
    # path('currency', currency, name='currency'),
    # path('smtp_settings', smtp_settings, name='smtp_settings'),
    # path('payment_methods', payment_methods, name='payment_methods'),
    # path('file_system_and_cache_configuration', file_system_and_cache_configuration,
    #      name='file_system_and_cache_configuration'),
    # path('social_media_logins', social_media_logins, name='social_media_logins'),
    # path('facebook/facebook_chat', facebook_chat, name='facebook_chat'),
    # path('facebook/facebook_comment', facebook_comment, name='facebook_comment'),
    # path('google/analytics_tools', analytics_tools, name='analytics_tools'),
    # path('google/google_recaptcha', google_recaptcha, name='google_recaptcha'),
    # path('google/google_map', google_map, name='google_map'),
    # path('google/google_firebase', google_firebase, name='google_firebase'),
    # path('server_status', server_status, name='server_status'),
]
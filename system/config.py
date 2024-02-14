import os

from django.urls import reverse
import threading

_thread_local = threading.local()


class GlobalConfig:
    def __init__(self):
        self.sms_api_url_for_token = os.getenv('SMS_API_URL_FOR_TOKEN',
                                               'https://idp.oss.net.bd/auth/realms/dev/protocol/openid-connect/token')
        self.sms_client_id = os.getenv('SMS_CLIENT_ID', 'cha-client')
        self.sms_client_secret = os.getenv('SMS_CLIENT_SECRET', '06811bee-461e-4f47-bf72-3d41d21a03af')
        self.sms_grant_type = os.getenv('SMS_GRANT_TYPE', 'client_credentials')
        self.email_api_url_for_send = os.getenv('EMAIL_API_URL_FOR_SEND',
                                                'https://testapi-k8s.oss.net.bd/api/broker-service/email/send_email')
        self.email_from_for_email_api = os.getenv('EMAIL_FROM_FOR_EMAIL_API', 'support@batworld.com')
        self.sms_api_url_for_send = os.getenv('SMS_API_URL_FOR_SEND',
                                              'https://api-k8s.oss.net.bd/api/broker-service/sms/send_sms')
        self.project_name = os.getenv('PROJECT_NAME', 'OSS-Framework')
        self.app_name = os.getenv('APP_NAME', 'Django')
        self.app_env = os.getenv('APP_ENV', 'production')

    @staticmethod
    def no_auth_url_list():
        no_auth_url_list = []
        from django.conf import settings
        return settings.NO_AUTH
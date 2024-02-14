import requests
from system.validation.number_validation import is_valid_phone_number
from apps.config.models import Configuration, config
from apps.sms.models import SmsGatewayConfiguration
import json


def send_sms(number=None, message=None, template=None):
    if number:
        if is_valid_phone_number(number):
            if template:
                body = template
            else:
                if message:
                    body = message
                else:
                    raise ValueError('Message body not Define : [Error: M101]')
            if config().otp_config == '1':
                send_sms_through_am_sms(number=number, message=body)
            elif config().otp_config == '2':
                send_sms_through_bulk_sms(number=number, message=body)
            else:
                raise ValueError("Otp Configuration not Active :  [Error: M101]")

        else:
            raise ValueError("This phone number is not valid :  [Error: M102]")
    else:
        raise ValueError("Number not found in SMS Request : [Error: M103]")


def send_sms_through_am_sms(number=None, message=None):
    gateway = SmsGatewayConfiguration.objects.filter(gateway_name='am_sms').first()
    api = gateway.api_url
    api_key = gateway.api_key
    device_id = gateway.device_id

    if api and api_key and device_id:
        parameters = {
            'message': str(message),
            'mobile_number': number,
            'device': device_id,
        }
        headers = {
            'apikey': str(api_key),
        }

        response = requests.post(api, headers=headers, data=parameters)
        if response.status_code == 200:
            response_body = json.loads(response.text)
            if response_body.get('code') == '200':
                result = response.text
                print(response_body.get('message'))
            else:
                print(response_body.get('message'), response_body.get('errors'))
        else:
            raise ValueError(f"Request failed with status code {response.status_code} [Error: M104]")


def send_sms_through_bulk_sms(number=None, message=None):
    gateway = SmsGatewayConfiguration.objects.filter(gateway_name='fast2sms').first()
    api = gateway.api_url
    username = gateway.user_name
    password = gateway.password

    data = {
        "api_key": password,
        "senderid": username,
        "number": number,
        "message": message,
        "type": 'text'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(api, data=data, headers=headers)

    print(response.text.encode('utf8'))

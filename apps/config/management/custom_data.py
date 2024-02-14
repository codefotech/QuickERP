from django.apps import apps
from apps.user.models import UserTypes
from django.db import connection
from django.core.management.base import BaseCommand
from apps.sms.models import SmsGatewayConfiguration


def user_type_data_migrate():
    user_type_model = apps.get_model('user', 'UserTypes')
    user_types_data = [
        {'name': 'General', 'code': 'G-1001', 'status': '1'},
        {'name': 'System Admin', 'code': 'SA-2002', 'status': '1'},
        {'name': 'Super Admin', 'code': 'SUA-3003', 'status': '1'},
        {'name': 'General Admin', 'code': 'GA-4004', 'status': '1'},
        {'name': 'Reseller', 'code': 'RS-5005', 'status': '1'},
        {'name': 'Sub Reseller', 'code': 'SR-6006', 'status': '1'}
    ]

    if user_type_model:
        UserTypes.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE user_types AUTO_INCREMENT = 1;")
            BaseCommand().stdout.write(BaseCommand().style.WARNING('Deleted all data from user_types table'))
        user_types_to_create = [item for item in user_types_data]
        if len(user_types_to_create) > 0:
            UserTypes.objects.bulk_create([UserTypes(**item) for item in user_types_to_create])
            BaseCommand().stdout.write(BaseCommand().style.SUCCESS('Initial data inserted successfully.'))
        else:
            BaseCommand().stdout.write(BaseCommand().style.WARNING('Migration already executed for user types model'))
    else:
        BaseCommand().stdout.write(
            BaseCommand().style.WARNING('UserTypes model does not exist. Make sure the migration is executed.'))


def sms_gateway_configuration_data_migrate():
    sms_gateway_configuration_model = apps.get_model('sms', 'SmsGatewayConfiguration')
    sms_gateway_configuration_data = [
        {'gateway_name': 'am_sms', 'api_url': '', 'api_key': '', 'device_id': '', 'user_name': '', 'password': ''},
        {'gateway_name': 'fast2sms', 'api_url': '', 'api_key': '', 'device_id': '', 'user_name': '', 'password': ''},
    ]

    if sms_gateway_configuration_model:  # Check if there is data to be saved
        existing_gateway_names = SmsGatewayConfiguration.objects.values_list('gateway_name', flat=True)

        sms_gateway_configuration_list = []

        for i in sms_gateway_configuration_data:
            gateway_name = i.get('gateway_name')

            if gateway_name not in existing_gateway_names:
                sms_gateway_configuration_list.append(SmsGatewayConfiguration(**i))

        if len(sms_gateway_configuration_list) > 0:
            SmsGatewayConfiguration.objects.bulk_create(sms_gateway_configuration_list)
            BaseCommand().stdout.write(BaseCommand().style.SUCCESS('Initial data inserted successfully.'))
        else:
            BaseCommand().stdout.write(
                BaseCommand().style.WARNING(f'Migration already executed for SmsGatewayConfiguration'))

    else:
        BaseCommand().stdout.write(
            BaseCommand().style.WARNING('SmsGatewayConfiguration model does not exist. Make sure the migration is '
                                        'executed.'))

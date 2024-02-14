from django.core.management.base import BaseCommand
from django.apps import apps

from apps.config.models import Configuration
from apps.user.models import UserTypes, Users
from django.db import connection
from django.utils import timezone
from datetime import datetime
from system.utils import hash_password
from apps.config.management.custom_data import user_type_data_migrate, sms_gateway_configuration_data_migrate

class Command(BaseCommand):
    help = 'Insert initial data into Model'

    def handle(self, *args, **options):
        # user_type data migrations
        user_type_data_migrate()
        sms_gateway_configuration_data_migrate()
        try:
            otp_config_model = apps.get_model('config', 'Configuration')
            if otp_config_model:
                if not Configuration.objects.filter(code='otp_config'):
                    config_data = {
                        'code': 'otp_config',
                        'value': '0',
                        'comments': '0=am_sms, 1=fast2sms',
                        'updated_by': '1',
                        'updated_at': timezone.now()
                    }
                    config = Configuration.objects.create(**config_data)
                    self.stdout.write(
                        self.style.SUCCESS(f'{config.code} Created Created Successfully'))
                else:
                    self.stdout.write(
                        self.style.SUCCESS('otp config already added!!'))
            else:
                self.stdout.write(
                    self.style.WARNING('Configuration model does not exist. Make sure the migration is executed.'))

        except Exception as err:
            self.stdout.write(
                self.style.WARNING(f'Error Raised, {str(err)} ..'))

        user_model = apps.get_model('user', 'users')
        if user_model:
            if not Users.objects.filter(email='sysadmin@gmail.com').exists():
                system_admin_data = {
                    'user_type': 'SA-2002',
                    'email': 'sysadmin@gmail.com',
                    'username': 'System Admin',
                    'user_mobile': '+8801521739742',
                    'password': hash_password('isp@12345'),
                    'user_status': '1'
                }
                system_admin = Users.objects.create(**system_admin_data)
                self.stdout.write(
                    self.style.SUCCESS(f'{system_admin.username} System Admin Created Successfully'))
            else:
                system_admin_data = {
                    'user_type': 'SA-2002',
                    'email': 'sysadmin@gmail.com',
                    'username': 'System Admin',
                    'user_mobile': '+8801521739742',
                    'password': hash_password('isp@12345')
                }
                system_admin = Users.objects.filter(email='sysadmin@gmail.com').first()
                system_admin.__dict__.update(system_admin_data)
                system_admin.save()
                self.stdout.write(self.style.WARNING(f'System Admin already Created !!!'))





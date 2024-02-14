from django.db import models


# Create your models here.

class SmsGatewayConfiguration(models.Model):
    gateway_name = models.CharField(max_length=255, default='', null=True, blank=True)
    api_url = models.CharField(max_length=255, default='', null=True, blank=True)
    api_key = models.CharField(max_length=255, default='', null=True, blank=True)
    device_id = models.CharField(max_length=255, default='', null=True, blank=True)
    user_name = models.CharField(max_length=255, default='', null=True, blank=True)
    password = models.CharField(max_length=255, default='', null=True, blank=True)

from django.db import models
from system.generic.models import BaseModel


# Create your models here.

class Configuration(BaseModel):
    code = models.CharField(max_length=50, default=None)
    value = models.CharField(max_length=200, default=None)
    comments = models.CharField(max_length=200, default=None)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)


def config():
    configs = Configuration.objects.all()
    config_data = {}
    for config in configs:
        config_data[config.code] = config.value

    my_object = ConfigObject(**config_data)

    return my_object


class ConfigObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BkashApiConfig(BaseModel):
    admin_id = models.IntegerField(unique=True)
    app_key = models.CharField(max_length=150, default=None)
    secret_key = models.CharField(max_length=150, default=None)
    user_name = models.CharField(max_length=150, default=None)
    password = models.CharField(max_length=150, default=None)
    sandbox_status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bkash_api_config'


class MobileAppConfig(BaseModel):
    version_name = models.CharField(max_length=150, default=None)
    apk = models.FileField(upload_to='mobile/apks')


class GeneralAdminConfig(BaseModel):
    subnet_mask = models.CharField(max_length=18, blank=True, null=True, default='')
    admin_id = models.CharField(max_length=20, blank=True, null=True, default='')
    router_list = models.TextField(null=True, blank=True, default='')
    hotspot_router_list = models.TextField(null=True, blank=True, default='')

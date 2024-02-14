from django.db import models

from apps.router.models import Router
from apps.seller.models import Seller
from system.generic.models import BaseModel
from django.db.models import Q


class RouterManager(models.Manager):
    def search_by_router_data(self, search_string):
        return self.get_queryset().filter(
            Q(name__contains=search_string) |
            Q(ip_address__contains=search_string) |
            Q(api_port__contains=search_string) |
            Q(user_name__contains=search_string)
        )


class HotspotRouter(BaseModel):
    name = models.CharField(max_length=20, blank=True, null=True)
    ip_address = models.CharField(max_length=254)
    api_port = models.CharField(max_length=50)
    ssh_port = models.CharField(max_length=50, default='')
    user_name = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True, null=True)
    version = models.CharField(max_length=200, blank=True, null=True)
    api_request_time = models.IntegerField(default=0, blank=True, null=True)
    admin_id = models.IntegerField(default=0, blank=True, null=True)
    status = models.IntegerField(default=1, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    REQUIRED_FIELDS = ['name', 'ip_address']

    class Meta:
        db_table = 'hotspot_routers'

    objects = RouterManager()


class UserHotspotRouter(BaseModel):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    router_list = models.TextField(null=True, blank=True, default='')
    admin_id = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_hotspot_router'


class HotspotActiveUser(BaseModel):
    router = models.ForeignKey(HotspotRouter, on_delete=models.CASCADE)
    user_list = models.JSONField(null=True, blank=True, default='')
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(default='', blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'hotspot_active_user'


class HotspotHostIpMac(BaseModel):
    mac_address = models.CharField(max_length=255, null=True, blank=True, default='')
    ip_address = models.CharField(max_length=255, null=True, blank=True, default='')
    comment = models.CharField(max_length=255, null=True, blank=True, default='')
    server = models.CharField(max_length=255, null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    router_id = models.IntegerField(default=None, blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'hotspot_host_ip_mac'

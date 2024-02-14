from django.db import models
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


class Router(BaseModel):
    name = models.CharField(max_length=20, blank=True, null=True)
    ip_address = models.CharField(max_length=254)
    api_port = models.CharField(max_length=50)
    ssh_port = models.CharField(default='', max_length=50)
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
        db_table = 'routers'

    objects = RouterManager()

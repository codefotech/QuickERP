from django.db import models
from system.generic.models import BaseModel
from django.db.models import Q


class IptvManager(models.Manager):
    def search_by_data(self, search_string):
        return self.get_queryset().filter(
            Q(name__icontains=search_string) |
            Q(url__icontains=search_string) |
            Q(order__icontains=search_string)
        )


class Iptv(BaseModel):
    name = models.CharField(max_length=20, blank=True, null=True, unique=True)
    url = models.CharField(max_length=254)
    image = models.TextField()
    order = models.CharField(max_length=255, blank=True, null=True)
    admin_id = models.IntegerField(default=0, blank=True, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)
    REQUIRED_FIELDS = ['name', 'url']

    class Meta:
        db_table = 'iptv'

    objects = IptvManager()

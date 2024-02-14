from django.db import models
from django.db.models import Q
from django.utils import timezone
from system.generic.models import BaseModel

class HotspotCustomerManager(models.Manager):
    def search_by_data(self, search_string):
        return self.get_queryset().filter(
            Q(name__icontains=search_string) |
            Q(mobile__icontains=search_string)
        )


# Create your models here.
class HotspotCustomer(BaseModel):
    name = models.CharField(max_length=100, unique=True, blank=True, null=True, default='')
    mobile = models.CharField(max_length=100, unique=True)
    package_expire_date = models.DateTimeField(default=timezone.now())
    admin_id = models.IntegerField(default=0, blank=True, null=True)
    otp_token = models.IntegerField(default=0, blank=True, null=True)
    otp_expire_time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(default=1, blank=True, null=True)
    mac_address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'hotspot_customer'

    objects = HotspotCustomerManager()


class HotspotCustomerToken(models.Model):
    customer_id = models.IntegerField()
    token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    expire_at = models.DateTimeField(default=timezone.now())
    status = models.IntegerField(default=1, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now())
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(default=timezone.now())
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'hotspot_customer_token'

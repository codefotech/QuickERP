from django.db import models

from apps.router.models import Router
from apps.seller.models import Seller
from apps.user.models import Users
from system.generic.models import BaseModel
from django.db.models import Q


class HotspotPackageManager(models.Manager):
    def search_by_data(self, search_string):
        return self.get_queryset().filter(
            Q(name__contains=search_string) |
            Q(profile__contains=search_string)
        )


class HotspotPackage(BaseModel):
    name = models.CharField(max_length=100, unique=False)
    day = models.CharField(max_length=100)
    price = models.CharField(max_length=100, default='0')
    admin_id = models.CharField(max_length=100, default=None)
    status = models.IntegerField(blank=True, null=True, default=1)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'hotspot_packages'

    objects = HotspotPackageManager()


class SellerHotspotPackage(BaseModel):
    package = models.ForeignKey(HotspotPackage, on_delete=models.CASCADE, blank=True, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank=True, null=True)
    admin = models.ForeignKey(Users,  on_delete=models.CASCADE, blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    customer_price = models.CharField(max_length=255, blank=True, null=True, default='0')
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'seller_hotspot_packages'


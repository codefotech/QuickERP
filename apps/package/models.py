from django.db import models

from apps.router.models import Router
from apps.seller.models import Seller
from apps.user.models import Users
from system.generic.models import BaseModel
from django.db.models import Q


class PackageManager(models.Manager):
    def search_by_data(self, search_string):
        return self.get_queryset().filter(
            Q(name__contains=search_string) |
            Q(profile__contains=search_string)
        )


class Package(BaseModel):
    name = models.CharField(max_length=100, unique=False)
    profile = models.CharField(max_length=100)
    router = models.ForeignKey(Router,  on_delete=models.CASCADE, blank=True, null=True)
    admin_id = models.CharField(max_length=100)
    status = models.IntegerField(blank=True, null=True, default=1)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'packages'

    objects = PackageManager()


class SellerPackage(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank=True, null=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, blank=True, null=True)
    admin = models.ForeignKey(Users,  on_delete=models.CASCADE, blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)

    class Meta:
        db_table = 'seller_packages'


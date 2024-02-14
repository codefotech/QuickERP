from datetime import datetime
from django.utils import timezone

from django.db import models

from apps.package.models import Package
from system.generic.models import BaseModel


# Create your models here.


class PPPOECustomer(BaseModel):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=100, blank=True)
    billing_type = models.CharField(max_length=100, blank=True)  # prepaid / postpaid
    pppoe_user = models.CharField(max_length=100, unique=True, blank=True)
    pppoe_password = models.CharField(max_length=100, blank=True)
    previous_package_id = models.CharField(max_length=100, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, blank=True, null=True)
    bill_amount = models.CharField(max_length=100, blank=True)
    billing_status = models.CharField(max_length=100, blank=True, default='0')
    billing_start_date = models.DateField(default=timezone.now, blank=True)
    bill_day = models.IntegerField(default=0, blank=True, null=True)
    auto_bill = models.IntegerField(default=0, blank=True, null=True)
    expire_at = models.DateTimeField(default=timezone.now, blank=True)
    admin_id = models.IntegerField(default=0, blank=True, null=True)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)
    updated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'pppoe_customer'



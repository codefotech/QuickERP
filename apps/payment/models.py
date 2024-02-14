from django.db import models
from system.generic.models import BaseModel


class WalletHistory(BaseModel):
    user_id = models.IntegerField()
    admin_id = models.IntegerField()
    amount = models.CharField(max_length=100)
    payment_type = models.IntegerField()
    payment_method = models.IntegerField()
    payment_details = models.TextField()
    approved = models.IntegerField(default=0)


class PackagePurchaseHistory(BaseModel):
    customer_id = models.IntegerField()
    package_id = models.IntegerField()
    admin_id = models.IntegerField()
    response = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'package_purchase_history'


class BkashPackagePurchaseRequest(BaseModel):
    package_id = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True, default=0)
    customer_id = models.IntegerField(null=True, blank=True)
    config_id = models.IntegerField(default=0, null=True)
    payment_id = models.TextField(null=True, blank=True)
    invoice_no = models.TextField(null=True, blank=True)
    transaction_id = models.TextField(null=True, blank=True, default='')
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bkash_payment_purchase_request'

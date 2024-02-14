from django.db import models

from apps.hotspot_customer.models import HotspotCustomer


# Create your models here.

class HotspotCard(models.Model):
    code = models.CharField(max_length=16, unique=True)
    validity = models.IntegerField()
    admin_id = models.IntegerField()
    status = models.IntegerField()
    customer = models.ForeignKey(HotspotCustomer,  on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hotspot_card'

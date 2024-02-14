from django.db import models

from main import settings
from system.generic.models import BaseModel
from django.db.models import Q


class SellerManager(models.Manager):
    def search_by_data(self, search_string):
        return self.get_queryset().filter(
            Q(user__email__icontains=search_string) |
            Q(user__username__icontains=search_string)
        )


class Seller(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    router_id = models.CharField(max_length=20, default='0', blank=True, null=True)
    minimum_bill_day = models.CharField(max_length=200, blank=True, null=True, default='0')
    free_user_create_deadline = models.IntegerField(blank=True, null=True, default=1)
    admin_id = models.CharField(max_length=20, blank=True, null=True, default='0')
    inactive = models.IntegerField(blank=True, null=True, default='0')
    subnet_mask = models.CharField(max_length=18, blank=True, null=True, default='')
    REQUIRED_FIELDS = ['name', 'router_id', 'admin_id', 'inactive']

    class Meta:
        db_table = 'sellers'

    objects = SellerManager()

    @property
    def mobile(self):
        self.user.user_mobile


class SellerExpense(BaseModel):
    expense_type = models.CharField(max_length=20)
    expense_amount = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=20)
    expense_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    expense_by = models.CharField(max_length=20)

from django import forms

from apps.package.models import Package, SellerPackage
from apps.seller.models import Seller
from system.generic.forms import CustomForm
from apps.pppoe_customer.models import PPPOECustomer
from system.config import _thread_local


class PPPoeCustomerAddForm(CustomForm):
    name = forms.CharField(required=True)
    mobile = forms.CharField(required=True)
    address = forms.CharField(required=True)
    # billing_type = forms.CharField(required=True)
    auto_bill = forms.IntegerField(required=True)
    pppoe_user = forms.CharField(required=True)
    pppoe_password = forms.CharField(required=True)
    package_id = forms.CharField(required=True)
    bill_amount = forms.CharField(required=True)
    bill_day = forms.CharField(required=True)
    billing_status = forms.CharField(required=False)
    # billing_start_date = forms.DateField(required=True)
    admin_id = forms.IntegerField(required=False)

    class Meta:
        model = PPPOECustomer
        fields = ['name', 'mobile', 'admin_id', 'address', 'billing_type',
                  'pppoe_user', 'pppoe_password', 'package_id', 'bill_amount', 'billing_start_date', 'auto_bill',
                  'billing_status', 'bill_day', 'expire_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PPPoeCustomerAddForm, self).clean()
        if _thread_local.user.user_type != 'SA-2002' and _thread_local.user.user_type != 'SUA-3003':
            cleaned_data['admin_id'] = _thread_local.user.id

        package_id = self.cleaned_data.get('package_id')
        if package_id:
            self.instance.package = Package.objects.get(id=package_id)
        if _thread_local.user.user_type == 'RS-5005':
            seller = Seller.objects.filter(user_id=_thread_local.user.id).first()
            package = SellerPackage.objects.filter(package_id=package_id, seller_id=seller.id).first()
            if float(package.price) > float(self.cleaned_data.get('bill_amount')):
                self.add_error('bill_amount', "Bill amount must be greater than package price")

            if int(seller.minimum_bill_day) > int(self.cleaned_data.get('bill_day')):
                self.add_error('bill_day', f"Bill day must be greater than {int(seller.minimum_bill_day)} day")

        return cleaned_data

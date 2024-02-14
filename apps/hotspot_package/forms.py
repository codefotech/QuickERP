from django import forms
from system.generic.forms import CustomForm
from .models import HotspotPackage, SellerHotspotPackage
from system.config import _thread_local
from ..seller.models import Seller


class HotspotPackageAddForm(CustomForm):
    name = forms.CharField(required=True)
    day = forms.CharField(required=True)
    admin_id = forms.IntegerField(required=False)

    class Meta:
        model = HotspotPackage
        fields = ['name', 'day', 'price', 'admin_id']

    def clean(self):
        cleaned_data = super(HotspotPackageAddForm, self).clean()
        cleaned_data['admin_id'] = _thread_local.user.id
        return cleaned_data

    def clean_price(self):
        price = self.cleaned_data['price']
        if float(price) <= 0:
            raise forms.ValidationError('Price cannot be negative or zero')
        return price

class AssignHotspotPackageForm(CustomForm):
    seller_id = forms.CharField(required=True)
    package_id = forms.CharField(required=True)
    admin_id = forms.IntegerField(required=False)
    price = forms.CharField(required=True)

    class Meta:
        model = SellerHotspotPackage
        fields = ['package_id', 'price', 'admin_id', 'seller_id', 'created_by', 'created_at']

    def clean_package_id(self):
        package_id = self.data.get('package_id')
        seller_id = self.data.get('seller_id')

        seller_package = None
        if not self.instance.id:
            seller_package = SellerHotspotPackage.objects.filter(package_id=package_id, seller_id=seller_id).first()

        if seller_package:
            raise forms.ValidationError("This Hotspot Router is already exist")
        else:
            return self.cleaned_data['package_id']

    def clean(self):
        cleaned_data = super(AssignHotspotPackageForm, self).clean()
        self.instance.admin = _thread_local.user
        package_id = self.cleaned_data.get('package_id')
        if package_id:
            self.instance.package = HotspotPackage.objects.get(id=package_id)
        seller_id = self.cleaned_data.get('seller_id')
        if seller_id:
            self.instance.seller = Seller.objects.get(id=seller_id)
        return cleaned_data

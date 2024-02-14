from django import forms
from system.generic.forms import CustomForm
from .models import Package, SellerPackage
from system.config import _thread_local
from ..router.models import Router
from ..seller.models import Seller


class PackageAddForm(CustomForm):
    name = forms.CharField(required=True)
    profile = forms.CharField(required=True)
    admin_id = forms.IntegerField(required=False)
    router_id = forms.IntegerField(required=True)

    class Meta:
        model = Package
        fields = ['name', 'profile', 'admin_id', 'router_id', 'status', 'created_by', 'created_at']

    def clean(self):
        cleaned_data = super(PackageAddForm, self).clean()
        print('ok')
        cleaned_data['admin_id'] = _thread_local.user.id
        router_id = self.cleaned_data.get('router_id')
        if router_id:
            self.instance.router = Router.objects.get(id=router_id)
        return cleaned_data


class AssignPackageForm(CustomForm):
    seller_id = forms.CharField(required=True)
    package_id = forms.CharField(required=True)
    admin_id = forms.IntegerField(required=False)
    price = forms.CharField(required=True)

    class Meta:
        model = SellerPackage
        fields = ['package_id', 'price', 'admin_id', 'seller_id', 'created_by', 'created_at']

    def clean_package_id(self):
        package_id = self.data.get('package_id')
        seller_id = self.data.get('seller_id')
        seller_package = None
        if not self.instance.id:
            seller_package = SellerPackage.objects.filter(package_id=package_id, seller_id=seller_id).first()


        if seller_package:
            raise forms.ValidationError("This Package is already assigned")
        else:
            return self.cleaned_data['package_id']

    def clean(self):
        cleaned_data = super(AssignPackageForm, self).clean()
        self.instance.admin = _thread_local.user
        package_id = self.cleaned_data.get('package_id')
        if package_id:
            self.instance.package = Package.objects.get(id=package_id)
        seller_id = self.cleaned_data.get('seller_id')
        if seller_id:
            self.instance.seller = Seller.objects.get(id=seller_id)
        return cleaned_data

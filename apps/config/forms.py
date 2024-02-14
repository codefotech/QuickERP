from django import forms

from apps.config.models import GeneralAdminConfig
from apps.seller.models import Seller
from system.generic.forms import CustomForm
from system.config import _thread_local


class AdminConfigUpdateForm(CustomForm):
    subnet_mask = forms.CharField(required=True)

    class Meta:
        model = GeneralAdminConfig
        fields = '__all__'

    def clean(self):
        cleaned_data = super(AdminConfigUpdateForm, self).clean()
        cleaned_data['admin_id'] = _thread_local.user.id
        return cleaned_data

    def clean_subnet_mask(self):
        data = self.cleaned_data['subnet_mask']
        if self.instance.id:
            seller_subnet = Seller.objects.filter(subnet_mask=data).exclude(
                subnet_mask=self.instance.subnet_mask).first()
            if seller_subnet:
                raise forms.ValidationError("This subnet mask already used with a seller")
            elif not seller_subnet:
                admin_subnet = GeneralAdminConfig.objects.filter(subnet_mask=data).exclude(
                    subnet_mask=self.instance.subnet_mask).first()
                if admin_subnet:
                    raise forms.ValidationError("This subnet mask already used by an admin")
        else:
            seller_subnet = Seller.objects.filter(subnet_mask=data).first()
            if seller_subnet:
                raise forms.ValidationError("This subnet mask already used with a seller")
            elif not seller_subnet:
                admin_subnet = GeneralAdminConfig.objects.filter(subnet_mask=data).first()
                if admin_subnet:
                    raise forms.ValidationError("This subnet mask already used by an admin")
        return data

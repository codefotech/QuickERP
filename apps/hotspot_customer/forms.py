from django import forms
from system.generic.forms import CustomForm
from apps.hotspot_customer.models import HotspotCustomer
from system.config import _thread_local


class HotspotCustomerAddForm(CustomForm):
    name = forms.CharField(required=True)
    mobile = forms.CharField(required=True)
    admin_id = forms.IntegerField(required=False)

    class Meta:
        model = HotspotCustomer
        fields = ['name', 'mobile', 'admin_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super(HotspotCustomerAddForm, self).clean()
        if _thread_local.user.user_type != 'SA-2002' and _thread_local.user.user_type != 'SUA-3003':
            cleaned_data['admin_id'] = _thread_local.user.id

        return cleaned_data

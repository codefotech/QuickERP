from django import forms
from system.generic.forms import CustomForm
from .models import Iptv
from system.config import _thread_local


class IptvAddForm(CustomForm):
    name = forms.CharField(required=True)
    url = forms.CharField(required=True)
    image = forms.CharField(required=False)
    created_by = forms.IntegerField(initial=0, required=False)
    updated_by = forms.IntegerField(initial=0, required=False)

    class Meta:
        model = Iptv
        fields = '__all__'
        error_messages = {
            'name':
                {
                    'unique': 'This IpTV is already Taken'
                },
            'url':
                {
                    'unique': 'This Url is not available'
                }
        }
    def clean(self):
        cleaned_data = super(IptvAddForm, self).clean()
        cleaned_data['admin_id'] = _thread_local.user.id
        return self.cleaned_data
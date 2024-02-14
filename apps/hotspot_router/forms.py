import json

from django import forms
from system.generic.forms import CustomForm
from .models import HotspotRouter, UserHotspotRouter
from system.config import _thread_local


class HotspotRouterAddForm(CustomForm):
    name = forms.CharField(required=True)
    ip_address = forms.CharField(required=True)
    api_port = forms.CharField(required=True)
    ssh_port = forms.CharField(required=True)
    user_name = forms.CharField(required=True)
    password = forms.CharField(required=True)
    created_by = forms.IntegerField(initial=0, required=False)
    updated_by = forms.IntegerField(initial=0, required=False)

    class Meta:
        model = HotspotRouter
        fields = '__all__'
        error_messages = {
            'user_name':
                {
                    'unique': 'This Router is already Taken'
                },
            'name':
                {
                    'unique': 'This Name is not available'
                }
        }

    def clean_name(self):
        if self.instance.id:
            router = HotspotRouter.objects.filter(name__exact=self.cleaned_data['name'],
                                           admin_id=_thread_local.user.id).exclude(
                name=self.cleaned_data['name']).first()
        else:
            router = HotspotRouter.objects.filter(name__exact=self.cleaned_data['name'],
                                           admin_id=_thread_local.user.id).first()
        if router:
            raise forms.ValidationError("This Hotspot Router is already exist")
        else:
            return self.cleaned_data['name']

    def clean(self):
        cleaned_data = super(HotspotRouterAddForm, self).clean()
        cleaned_data['admin_id'] = _thread_local.user.id
        return self.cleaned_data


class HotspotRouterAssignForm(CustomForm):
    class Meta:
        model = UserHotspotRouter
        fields = '__all__'

    def clean(self):
        cleaned_data = super(HotspotRouterAssignForm, self).clean()
        cleaned_data['admin_id'] = _thread_local.user.id
        return self.cleaned_data

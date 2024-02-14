from django import forms
from system.generic.forms import CustomForm
from system.router.main import Microtik
from system.utils import hash_password
from apps.seller.models import Seller
from ..router.models import Router
from ..user.models import Users
from django.db import transaction
from system.config import _thread_local


class ReSellerAddForm(CustomForm):
    user_mobile = forms.CharField(required=True)
    email = forms.CharField(required=True)
    username = forms.CharField(required=True)
    password = forms.CharField(required=False)
    hotspot_ip_range_start = forms.CharField(required=True)
    hotspot_ip_range_end = forms.CharField(required=True)

    class Meta:
        model = Seller
        fields = ['email', 'username', 'password', 'hotspot_ip_range_start', 'hotspot_ip_range_end', 'user_mobile', 'minimum_bill_day', 'user','admin_id', 'inactive']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set 'required' attribute of the 'user' field to False
        self.fields['user'].required = False

    def clean(self):
        cleaned_data = super(ReSellerAddForm, self).clean()
        cleaned_data['admin_id'] = _thread_local.user.id
        if not self.instance.user_id:
            password = cleaned_data.get('password')
            cleaned_data['password'] = hash_password(password)

        user_type = 'SR-6006'

        if hasattr(self.instance, 'user') and self.instance.user:
            user = Users.objects.get(id=self.instance.user_id)
            user.user_mobile = self.cleaned_data.get('user_mobile')
            user.username = self.cleaned_data.get('username')
            user.email = self.cleaned_data.get('email')
            user.user_type = user_type
            cleaned_data['user'] = user
            user.save()

        return cleaned_data

    def clean_username(self):
        # Your custom validation logic goes here
        data = self.cleaned_data['username']
        if self.instance.user_id:
            user = Users.objects.filter(username=data).exclude(username=self.instance.user.username).first()
            if user:
                raise forms.ValidationError("This user is already exist")
        else:
            user = Users.objects.filter(username=data).first()
            if user:
                raise forms.ValidationError("This user is already exist")
        return data



    def clean_email(self):
        # Your custom validation logic goes here
        data = self.cleaned_data['email']
        if self.instance.user_id:
            user = Users.objects.filter(email=data).exclude(email=self.instance.user.email).first()
            if user:
                raise forms.ValidationError("This email is already exist")
        else:
            user = Users.objects.filter(email=data).exclude(email=self.instance.user.email if hasattr(self.instance, 'user') and hasattr(self.instance.user, 'email') else '').first()
            if user:
                raise forms.ValidationError("This email is already exist")

        return data



    @transaction.atomic
    def save(self, *args, commit=True, **kwargs):
        if not self.instance.id:
            user_data = {
                'username': self.cleaned_data.get('username'),
                'user_mobile': self.cleaned_data.get('user_mobile'),
                'email': self.cleaned_data.get('email'),
                'password': self.cleaned_data.get('password'),
                'user_type': 'SR-6006'
            }
            user = Users.objects.create(**user_data)
            self.instance.user = user




        return super().save(commit=commit)

from django import forms
from system.generic.forms import CustomForm
from system.router.main import Microtik
from system.router.ssh_router import MikroTikSSHManager
from system.utils import hash_password
from .models import Seller
from ..config.models import GeneralAdminConfig
from ..router.models import Router
from ..user.models import Users
from django.db import transaction
from system.config import _thread_local


class SellerAddForm(CustomForm):
    user_mobile = forms.CharField(required=True)
    email = forms.CharField(required=True)
    username = forms.CharField(required=True)
    password = forms.CharField(required=False)
    subnet_mask = forms.CharField(required=True)

    class Meta:
        model = Seller
        fields = ['router_id', 'email', 'username', 'password', 'subnet_mask', 'user_mobile', 'minimum_bill_day',
                  'user', 'admin_id', 'inactive','free_user_create_deadline']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set 'required' attribute of the 'user' field to False
        self.fields['user'].required = False

    def clean(self):
        cleaned_data = super(SellerAddForm, self).clean()
        cleaned_data['admin_id'] = _thread_local.user.id
        if not self.instance.user_id:
            password = cleaned_data.get('password')
            cleaned_data['password'] = hash_password(password)

        if hasattr(self.instance, 'user') and self.instance.user:
            user = Users.objects.get(id=self.instance.user_id)
            user.user_mobile = self.cleaned_data.get('user_mobile')
            user.username = self.cleaned_data.get('username')
            user.email = self.cleaned_data.get('email')
            cleaned_data['user'] = user
            user.save()

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.instance.user_id:
            if not password:
                raise forms.ValidationError("Password is required")
        return password

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

    def clean_subnet_mask(self):
        data = self.cleaned_data['subnet_mask']
        if self.instance.id:
            seller_subnet = Seller.objects.filter(subnet_mask=data).exclude(
                subnet_mask=self.instance.subnet_mask).first()
            if seller_subnet:
                raise forms.ValidationError("This subnet mask already used with a seller")
            elif not seller_subnet:
                admin_subnet = GeneralAdminConfig.objects.filter(subnet_mask=data).first()
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

    def clean_router_id(self):
        router_id = self.cleaned_data['router_id']
        router = Router.objects.get(id=router_id)
        ip = router.ip_address
        port = router.ssh_port
        username = router.user_name
        password = router.password
        try:
            connection = MikroTikSSHManager.connect_router(ip,username,
                                                           password,
                                                           port)
            if not connection:
                raise forms.ValidationError(f"Router can't connect ")

        except Exception as e:
            raise forms.ValidationError(f"Router Error {e}")

        return router_id

    def clean_email(self):
        # Your custom validation logic goes here
        data = self.cleaned_data['email']
        if self.instance.user_id:
            user = Users.objects.filter(email=data).exclude(email=self.instance.user.email).first()
            if user:
                raise forms.ValidationError("This email is already exist")
        else:
            user = Users.objects.filter(email=data).exclude(
                email=self.instance.user.email if hasattr(self.instance, 'user') and hasattr(self.instance.user,
                                                                                             'email') else '').first()
            if user:
                raise forms.ValidationError("This email is already exist")

        return data

    @transaction.atomic
    def save(self, *args, commit=True, **kwargs):
        if not self.instance.id:
            user_type = 'RS-5005'
            if _thread_local.user.user_type == 'RS=5005':
                user_type = 'SR-6006'

            user_data = {
                'username': self.cleaned_data.get('username'),
                'user_mobile': self.cleaned_data.get('user_mobile'),
                'email': self.cleaned_data.get('email'),
                'password': self.cleaned_data.get('password'),
                'user_type': user_type
            }
            user = Users.objects.create(**user_data)
            self.instance.user = user

        return super().save(commit=commit)

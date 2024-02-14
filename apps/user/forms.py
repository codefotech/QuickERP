from django import forms
from system.generic.forms import CustomForm
from .models import Users
from system.utils import hash_password
from system.config import _thread_local


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.PasswordInput()


class UserAddForm(CustomForm):
    created_by = forms.IntegerField(initial=0, required=False)
    updated_by = forms.IntegerField(initial=0, required=False)
    user_status = forms.CharField(required=False)
    user_verification = forms.IntegerField(required=False)
    user_agreement = forms.IntegerField(required=False)
    nationality_type = forms.CharField(required=False)
    identity_type = forms.CharField(required=False)
    first_login = forms.IntegerField(required=False)
    is_approved = forms.IntegerField(required=False)
    security_profile_id = forms.IntegerField(required=False)
    user_type = forms.CharField(required=False)
    user_role = forms.CharField(required=False)
    password = forms.CharField(required=False)

    class Meta:
        model = Users
        fields = '__all__'
        error_messages = {
            'email':
                {
                    'unique': 'This email is already Taken'
                }
        }

    def clean(self):
        cleaned_data = super(UserAddForm, self).clean()
        if not self.instance.id:
            password = cleaned_data.get('password')
            cleaned_data['password'] = hash_password(password)
        else:
            cleaned_data['password'] = self.instance.password
        if _thread_local.user.user_type == 'SA-2002':
            cleaned_data['user_type'] = 'SUA-3003'
            cleaned_data['user_role'] = 4

        if _thread_local.user.user_type == 'SUA-3003':
            cleaned_data['user_type'] = 'GA-4004'
            cleaned_data['user_role'] = 5

        if _thread_local.user.user_type == 'GA-4004':
            cleaned_data['user_type'] = 'G-1001'
            cleaned_data['admin'] = _thread_local.user.id

        return self.cleaned_data

    def clean_user_role(self):
        user_role = self.cleaned_data.get('user_role')
        if not _thread_local.user.user_type == 'SA-2002' and not _thread_local.user.user_type == 'SUA-3003':
            if not user_role:
                raise forms.ValidationError("This field is required")
        return user_role

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password and not self.instance.id:
            raise forms.ValidationError("Password is required")
        return password


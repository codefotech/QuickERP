from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Q
from system.generic.models import BaseModel
from django.utils import timezone


class UserManager(models.Manager):
    def search_by_user_name(self, search_string):
        UserType = UserTypes.objects.filter(name__icontains=search_string).first()

        return self.get_queryset().filter(
            Q(username__icontains=search_string) |
            Q(email__icontains=search_string) |
            Q(user_type__icontains=UserType.id if UserType else search_string) |
            Q(user_status__icontains=search_string)
        )


class UserTypes(models.Model):
    name = models.CharField(max_length=255, default='General')
    code = models.CharField(max_length=255, default='G-1001')
    permission = models.JSONField(default={})
    status = models.CharField(max_length=8)

    class Meta:
        db_table = 'user_types'


class Users(AbstractBaseUser, BaseModel):
    class UserVerification(models.TextChoices):
        yes = 'yes'
        no = 'no'

    class UserGender(models.TextChoices):
        male = 'Male'
        female = 'Female'
        not_defined = 'Not defined'

    # user_type
    # {'name': 'General', 'code': 'G-1001', 'status': '1'},
    # {'name': 'System Admin', 'code': 'SA-2002', 'status': '1'},
    # {'name': 'Super Admin', 'code': 'SUA-3003', 'status': '1'},
    # {'name': 'General Admin', 'code': 'GA-4004', 'status': '1'},
    # {'name': 'Reseller', 'code': 'RS-5005', 'status': '1'},
    # {'name': 'Sub Reseller', 'code': 'GA-6006', 'status': '1'}
    username = models.CharField(max_length=255, unique=True)
    user_type = models.CharField(max_length=10)
    email = models.CharField(unique=True, max_length=254)
    designation = models.CharField(max_length=200, blank=True, null=True)
    password = models.CharField(max_length=250, blank=True, null=True)
    user_hash = models.TextField(blank=True, default=0)
    user_status = models.CharField(max_length=1, default=1)
    user_verification = models.CharField(max_length=8, choices=UserVerification.choices, default=UserVerification.no)
    pin_number = models.CharField(max_length=200, blank=True, null=True)
    user_pic = models.TextField(blank=True)
    user_nid = models.CharField(max_length=32, blank=True, null=True)
    user_tin = models.CharField(max_length=20, blank=True, null=True)
    user_gender = models.CharField(max_length=11, blank=True, null=True, choices=UserGender.choices,
                                   default=UserGender.not_defined)
    user_mobile = models.CharField(max_length=20, blank=True, null=True)
    passport_nid_file = models.CharField(max_length=70, blank=True, null=True)
    signature = models.TextField(blank=True, null=True)
    signature_encode = models.TextField(blank=True, null=True)
    user_first_login = models.DateTimeField(blank=True, null=True)
    user_language = models.CharField(max_length=10, blank=True, default='bn')
    security_profile_id = models.IntegerField(default=1)
    division = models.IntegerField(blank=True, null=True)
    district = models.IntegerField(blank=True, null=True)
    thana = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=20, blank=True, null=True)
    passport_no = models.CharField(max_length=20, blank=True, null=True)
    contact_address = models.CharField(max_length=250, blank=True, null=True)
    post_code = models.CharField(max_length=20, blank=True, null=True)
    remember_token = models.CharField(max_length=100, blank=True, null=True)
    login_token = models.CharField(max_length=255, blank=True, null=True)
    user_hash_expire_time = models.DateTimeField(blank=True, null=True)
    auth_token_allow = models.IntegerField(default=0, blank=True, null=True)
    auth_token = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    super_admin = models.IntegerField(default=0, blank=True, null=True)
    admin = models.IntegerField(default=0, blank=True, null=True)
    reseller = models.IntegerField(default=0, blank=True, null=True)
    sub_reseller = models.IntegerField(default=0, blank=True, null=True)
    first_login = models.IntegerField(default=0)
    otp_expire_time = models.DateTimeField(blank=True, null=True)
    is_approved = models.IntegerField(default=0)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(default=0)  # need to remove default = 0
    last_login = models.DateTimeField(blank=True, null=True)
    user_role = models.IntegerField(blank=True, null=True)
    wallet_balance = models.CharField(max_length=100, blank=True, null=True, default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    objects: UserManager = UserManager()

    @property
    def name(self):
        return self.username

    @property
    def user_type_name(self):
        if self.user_type:
            user_type_name = UserTypes.objects.filter(code=self.user_type).first().name
        else:
            user_type_name = ''
        return user_type_name

    @property
    def user_role_name(self):
        if self.user_role == 1:
            return 'Manager'
        elif self.user_role == 2:
            return 'Staff'
        else:
            return 'Store'

    @property
    def status(self):
        if self.user_status == '0':
            return 'Inactive'
        elif self.user_status == '1':
            return 'Active'

    @property
    def is_sysadmin(self):
        if self.user_type == 'SA-2002':
            return True
        else:
            return False

    @property
    def is_supadmin(self):
        if self.user_type == 'SUA-3003':
            return True
        else:
            return False

    @property
    def is_general(self):
        if self.user_type == 'G-1001':
            return True
        else:
            return False

    @property
    def is_reseller(self):
        if self.user_type == 'R-5005':
            return True
        else:
            return False

    @property
    def is_subreseller(self):
        if self.user_type == 'GA-6006':
            return True
        else:
            return False

    def __str__(self):
        return self.username

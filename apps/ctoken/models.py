from django.db import models
from django.utils import timezone


class Token(models.Model):
    token = models.CharField(max_length=500)
    app_id = models.IntegerField() # Change this according to your user model
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    @property
    def is_expired(self):
        return timezone.now() > self.expired_at


class AppKey(models.Model):
    app_name = models.CharField(max_length=100)
    app_key = models.CharField(max_length=100, unique=True)
    secret_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.app_key} - {self.app_name}"

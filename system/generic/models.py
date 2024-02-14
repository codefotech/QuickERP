from django.db import models
from system.config import _thread_local
from datetime import datetime


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        if self.id:
            if hasattr(self, 'updated_by'):
                if hasattr(_thread_local, 'user'):
                    if _thread_local.user.is_anonymous:
                        self.updated_by = '0'
                    else:
                        self.updated_by = _thread_local.user.id
                else:
                    self.updated_by = '0'
            if hasattr(self, 'updated_at'):
                self.updated_at = datetime.now()
        else:
            if hasattr(self, 'created_by'):
                if hasattr(_thread_local, 'user'):
                    if _thread_local.user.is_anonymous:
                        self.created_by = '0'
                    else:
                        self.created_by =_thread_local.user.id
                else:
                    self.created_by = '0'
            if hasattr(self, 'created_at'):
                self.created_at = datetime.now()
            if hasattr(self, 'updated_by'):
               if hasattr(_thread_local, 'user'):
                   if _thread_local.user.is_anonymous:
                       self.updated_by = '0'
                   else:
                       self.updated_by = _thread_local.user.id
               else:
                   self.updated_by = '0'

            if hasattr(self, 'updated_at'):
                self.updated_at = datetime.now()

        super(BaseModel, self).save(*args, **kwargs)


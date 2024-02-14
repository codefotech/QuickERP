from django.urls import path, include
from .log_view import LogStreamView

urlpatterns = [
    path('logstream/', LogStreamView.as_view(), name='logstream'),
    path('log_view/', LogStreamView().log, name='logstream'),
]

"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from apps.router.router_os import consumers

application = ProtocolTypeRouter(dict(http=get_asgi_application(), websocket=URLRouter([
    re_path('ws/send/$', consumers.TestConsumer.as_asgi()),
    re_path('ws/router_data/$', consumers.RouterDataConsumer.as_asgi()),

])))

from django.conf import settings
from system.config import _thread_local
from system.utils import prepare_menu_item


def global_context_processor(request):
    context_data = {
        'user_type': _thread_local.user.user_type if hasattr(_thread_local.user, 'user_type') else '',
    }
    context = {'config': context_data,
               'user': _thread_local.user,
               'MEDIA': '/media/',
               'menu_items': prepare_menu_item()
               }

    return context

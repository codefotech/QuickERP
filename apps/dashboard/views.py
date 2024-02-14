from django.shortcuts import render

from apps.ctoken.models import Token
from apps.hotspot_customer.tasks import ssh_router_user_add_remove, update_hotspot_customer_mac
from apps.hotspot_router.tasks import update_hotspot_router_user, update_hotspot_mac_ip
from apps.pppoe_customer.tasks import update_pppoe_customer_package
from system.router.ssh_router import MikroTikSSHManager


# Create your views here.
def dashboard(request):

    # ssh_router_user_add_remove()
    # update_hotspot_customer_mac()
    # update_hotspot_mac_ip()
    # update_pppoe_customer_package()
    context = {'total_apps_token': ''}
    if request.user.user_type == 'SA-2002':
        context['total_app_token'] = Token.objects.all().count()
    return render(request, 'backend/index.html', context=context)

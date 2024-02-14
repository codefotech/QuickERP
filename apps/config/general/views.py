from datetime import datetime
import io

from django.http import HttpResponse
from django.shortcuts import render, redirect
import os

from apps.config.forms import AdminConfigUpdateForm
from apps.config.models import Configuration, MobileAppConfig, GeneralAdminConfig
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from apps.hotspot_customer.tasks import ssh_router_user_add_remove, update_hotspot_customer_mac
from apps.hotspot_router.models import HotspotRouter
from apps.hotspot_router.tasks import update_hotspot_mac_ip
from apps.router.models import Router
from system.utils import CommonFunction


def app_settings(request, *args, **kwargs):
    config = MobileAppConfig.objects.first()
    if request.POST:
        if not config:
            config = MobileAppConfig()
        fs = FileSystemStorage()
        if request.FILES['apk']:
            myfile = request.FILES['apk']
            filename = fs.save(myfile.name, myfile)
            uploaded_file = fs.url(filename)
            config.apk = uploaded_file

        config.version_name = request.POST.get('version')
        config.save()

    context = {'config': config}
    return render(request, 'backend/system/settings/general_settings/mobile_app_version_update.html', context)


def admin_general_settings(request, *args, **kwargs):
    general_config = GeneralAdminConfig.objects.filter(admin_id=request.user.id).first()
    form = AdminConfigUpdateForm(instance=general_config)
    if request.POST:
        form = AdminConfigUpdateForm(request.POST.copy())
        if general_config:
            form = AdminConfigUpdateForm(request.POST.copy(), instance=general_config)

        if request.method == 'POST':
            form.data['router_list'] = request.POST.getlist('router_list[]')
            form.data['hotspot_router_list'] = request.POST.getlist('hotspot_router_list[]')
            if form.is_valid():
                if form.is_valid():
                    form.save(commit=True)
                    return redirect('admin_general_settings')

    context = {'general_config': general_config, 'form': form}
    query1 = HotspotRouter.objects.filter(status=1, admin_id=request.user.id)
    context['hotspot_router'] = CommonFunction.model_to_dict(model=None, key='id', value='name', query=query1)
    query2 = Router.objects.filter(status=1, admin_id=request.user.id)
    context['router'] = CommonFunction.model_to_dict(model=None, key='id', value='name', query=query2)

    return render(request, 'backend/system/settings/general_settings/general_admin_settings.html', context=context)


def ssh_router_user_add_remove_cron(request):
    ssh_router_user_add_remove()
    return HttpResponse('command runned')


def update_hotspot_customer_mac_cron(request):
    update_hotspot_customer_mac()
    return HttpResponse('command runned')


def update_hotspot_mac_ip_cron(request):
    update_hotspot_mac_ip()
    return HttpResponse('command runned')

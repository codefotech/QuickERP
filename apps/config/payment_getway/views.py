import json

from django.http import JsonResponse
from django.shortcuts import render

from apps.config.models import BkashApiConfig


def bkash_config(request):
    config = BkashApiConfig.objects.filter(admin_id=request.user.id).first()
    if request.method == "POST":
        message = 'Bkash Configuration Updated'
        if not config:
            config = BkashApiConfig(admin_id=request.user.id)
            message = 'Bkash Configuration Added'

        config.app_key = request.POST.get('app_key')
        config.secret_key = request.POST.get('secret_key')
        config.user_name = request.POST.get('user_name')
        config.password = request.POST.get('password')

        if request.POST.get('sandbox_status') == 'on':
            config.sandbox_status = 1
        else:
            config.sandbox_status = 0

        config.save()

        return JsonResponse({'message': message})

    context = {'config': config}
    return render(request, 'backend/system/payment-gateway/bkash_config.html', context)

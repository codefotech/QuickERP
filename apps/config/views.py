from django.shortcuts import render
from apps.config.models import Configuration, config
from django.http import JsonResponse

from apps.sms.models import SmsGatewayConfiguration


# Create your views here.


def otp_configuration(request):
    otp_config = config().otp_config
    amsms_otp = False
    fast2sms_otp = False
    if otp_config == '1':
        amsms_otp = True
    elif otp_config == '2':
        fast2sms_otp = True

    context = {
        'amsms_otp': amsms_otp,
        'fast2sms_otp': fast2sms_otp
    }
    return render(request, 'backend/system/otp-system/otp_configuration.html', context)


def otp_configuration_update(request):
    if request.POST:
        config = Configuration.objects.filter(code='otp_config').first()
        if request.POST.get('config') == 'amsms_otp':
            config.value = 1
            config.save()
            return JsonResponse({'message': 'OTP Configuration AMSMS OTP Status ON'})

        elif request.POST.get('config') == 'fast2sms_otp':
            config.value = 2
            config.save()
            return JsonResponse({'message': 'OTP Configuration Fast2SMS OTP OTP Status ON'})


def sms_template(request):
    from system.sms.send_sms import send_sms
    send_sms('+8801854422750', 'Hello 123')
    return render(request, 'backend/system/otp-system/sms_template.html')


def set_otp_credentials(request):
    am_sms = SmsGatewayConfiguration.objects.filter(gateway_name='am_sms').first()
    fast2sms = SmsGatewayConfiguration.objects.filter(gateway_name='fast2sms').first()
    context = {
        'am_sms': am_sms,
        'fast2sms': fast2sms
    }
    return render(request, 'backend/system/otp-system/set_otp_credentials.html', context=context)

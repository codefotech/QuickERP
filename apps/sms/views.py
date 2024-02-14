from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SmsGatewayConfiguration


@csrf_exempt  # Use this decorator for simplicity. Consider implementing proper CSRF protection.
def save_sms_gateway_config(request):
    if request.method == 'POST':
        try:
            gateway_name = request.POST.get('gateway_name')
            gateway = SmsGatewayConfiguration.objects.filter(gateway_name=gateway_name).first()
            api_url = request.POST.get('api_url')
            api_key = request.POST.get('api_key')
            device_id = request.POST.get('device_id')
            user_name = request.POST.get('user_name')
            password = request.POST.get('password')

            # Create a new SmsGatewayConfiguration object and save it to the database
            gateway.api_url = api_url
            gateway.api_key = api_key
            gateway.device_id = device_id
            gateway.user_name = user_name
            gateway.password = password
            gateway.save()

            return JsonResponse({'success': True, 'message': 'Data saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

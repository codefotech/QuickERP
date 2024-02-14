from django.http import JsonResponse
from .models import AppKey  # Assuming you have a model for AppKey
from .models import Token  # Assuming you have a model for Token
from system.auth.api import generate_token  # Your token generation function from previous examples
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def generate_token_api(request):
    if request.method == 'POST':
        app_key = request.POST.get('app_key')
        secret_key = request.POST.get('secret_key')

        try:
            app = AppKey.objects.filter(app_key=app_key, secret_key=secret_key).first()
            if app:
                app_id = app.id
                token = generate_token(app_id)
                expiration_time = timedelta(days=180)
                expired_at = timezone.now() + expiration_time

                new_token = Token.objects.create(token=token, app_id=app_id, expired_at=expired_at)
                new_token.save()

                return JsonResponse({'token': token})
            else:
                return JsonResponse({'error': 'Invalid app key or secret key'}, status=401)

        except AppKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid app key or secret key'}, status=401)


    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def check_token_api(request):
    if request.method == 'POST':
        # Get the token from the Authorization header
        authorization_header = request.headers.get('Authorization')
        if not authorization_header or not authorization_header.startswith('Bearer '):
            return JsonResponse({'error': 'Invalid authorization header'}, status=401)

        token = authorization_header.split('Bearer ')[1]

        try:
            stored_token = Token.objects.get(token=token)
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        if stored_token.is_expired:
            return JsonResponse({'error': 'Token has expired'}, status=401)

        return JsonResponse({'message': 'Token is valid'})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)




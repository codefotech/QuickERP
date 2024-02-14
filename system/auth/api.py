import jwt
from django.utils import timezone
from jwt.exceptions import ExpiredSignatureError, DecodeError
from django.conf import settings
from functools import wraps
from django.http import JsonResponse
from datetime import datetime, timedelta

from apps.ctoken.models import Token

SECRET_KEY = settings.SECRET_KEY


def generate_token(data):
    payload = {
        'data': data,
        'exp':  timezone.now() + timedelta(days=180)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except ExpiredSignatureError:
        return None  # Token is expired
    except DecodeError:
        return None


def token_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        token = auth_header.split(' ')[1]

        tokens = Token.objects.filter(token=token).first()
        if tokens:
            if tokens.expired_at < datetime.now():
                return JsonResponse({'error': 'Expired token'}, status=401)
        else:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        decoded_token = verify_token(token)
        return view_func(request, *args, **kwargs)

    return wrapped_view

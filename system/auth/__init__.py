from apps.user.models import Users
from system.utils import verify_password

def authenticate_user(email, password):
    try:
        user = Users.objects.get(email=email)
    except Users.DoesNotExist:
        return None
    try:
        hashed_password = user.password.encode('utf-8')
    except Exception:
        raise Exception("Password is not given for the user")
    if verify_password(password, hashed_password):
        return user
    else:
        return None


def authenticate_user_by_id(id=None):
    try:
        user = Users.objects.get(id=id)
        return user
    except Users.DoesNotExist:
        return None


from django.core.exceptions import ValidationError
def password_validation(value):
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
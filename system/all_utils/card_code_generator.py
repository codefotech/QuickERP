import secrets
import string


def generate_random_code():
    digits = string.digits  # Define the characters pool with digits only
    code_length = 12  # Length of the code
    return ''.join(secrets.choice(digits) for _ in range(code_length))

import re


def is_valid_phone_number(phone_number):
    # Define a regex pattern for the desired format with 13 digits

    # Use the re.match function to check if the phone_number matches the pattern
    if phone_number.startswith("+88") and len(phone_number) == 14:
        return True
    else:
        return False

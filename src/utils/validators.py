"""
Validators utility module.
This module provides utilities for validating data.
"""
import re
import logging
from typing import Any, Callable, Dict, List, Optional, Pattern, TypeVar, Union, cast

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')


class ValidationError(Exception):
    """
    Exception raised for validation errors.
    """
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: The email address to validate.
    
    Returns:
        True if the email is valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    
    Args:
        phone: The phone number to validate.
    
    Returns:
        True if the phone number is valid, False otherwise.
    """
    # Remove spaces, dashes, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if the phone number is valid
    pattern = r'^(\+\d{1,3})?(\d{10,15})$'
    return bool(re.match(pattern, phone))


def validate_url(url: str) -> bool:
    """
    Validate a URL.
    
    Args:
        url: The URL to validate.
    
    Returns:
        True if the URL is valid, False otherwise.
    """
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_ip(ip: str) -> bool:
    """
    Validate an IP address.
    
    Args:
        ip: The IP address to validate.
    
    Returns:
        True if the IP address is valid, False otherwise.
    """
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    ipv4_match = re.match(ipv4_pattern, ip)
    
    if ipv4_match:
        # Check if each octet is between 0 and 255
        for octet in ipv4_match.groups():
            if int(octet) > 255:
                return False
        return True
    
    # IPv6 pattern
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    return bool(re.match(ipv6_pattern, ip))


def validate_date(date: str, format: str = '%Y-%m-%d') -> bool:
    """
    Validate a date string.
    
    Args:
        date: The date string to validate.
        format: The expected date format.
    
    Returns:
        True if the date is valid, False otherwise.
    """
    try:
        import datetime
        datetime.datetime.strptime(date, format)
        return True
    except ValueError:
        return False


def validate_time(time: str, format: str = '%H:%M:%S') -> bool:
    """
    Validate a time string.
    
    Args:
        time: The time string to validate.
        format: The expected time format.
    
    Returns:
        True if the time is valid, False otherwise.
    """
    try:
        import datetime
        datetime.datetime.strptime(time, format)
        return True
    except ValueError:
        return False


def validate_datetime(dt: str, format: str = '%Y-%m-%d %H:%M:%S') -> bool:
    """
    Validate a datetime string.
    
    Args:
        dt: The datetime string to validate.
        format: The expected datetime format.
    
    Returns:
        True if the datetime is valid, False otherwise.
    """
    try:
        import datetime
        datetime.datetime.strptime(dt, format)
        return True
    except ValueError:
        return False


def validate_credit_card(card_number: str) -> bool:
    """
    Validate a credit card number using the Luhn algorithm.
    
    Args:
        card_number: The credit card number to validate.
    
    Returns:
        True if the credit card number is valid, False otherwise.
    """
    # Remove spaces and dashes
    card_number = re.sub(r'[\s\-]', '', card_number)
    
    # Check if the card number contains only digits
    if not card_number.isdigit():
        return False
    
    # Check if the card number has a valid length
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    
    # Luhn algorithm
    digits = [int(d) for d in card_number]
    checksum = 0
    
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    
    return checksum % 10 == 0


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = True
) -> bool:
    """
    Validate password strength.
    
    Args:
        password: The password to validate.
        min_length: Minimum password length.
        require_uppercase: Whether to require at least one uppercase letter.
        require_lowercase: Whether to require at least one lowercase letter.
        require_digit: Whether to require at least one digit.
        require_special: Whether to require at least one special character.
    
    Returns:
        True if the password meets the requirements, False otherwise.
    """
    # Check minimum length
    if len(password) < min_length:
        return False
    
    # Check for uppercase letters
    if require_uppercase and not any(c.isupper() for c in password):
        return False
    
    # Check for lowercase letters
    if require_lowercase and not any(c.islower() for c in password):
        return False
    
    # Check for digits
    if require_digit and not any(c.isdigit() for c in password):
        return False
    
    # Check for special characters
    if require_special and not any(not c.isalnum() for c in password):
        return False
    
    return True


def validate_required(value: Any, field_name: str) -> None:
    """
    Validate that a value is not None or empty.
    
    Args:
        value: The value to validate.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the value is None or empty.
    """
    if value is None:
        raise ValidationError(f"Le champ {field_name} est requis.", field_name)
    
    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"Le champ {field_name} ne peut pas être vide.", field_name)
    
    if isinstance(value, (list, dict, set)) and not value:
        raise ValidationError(f"Le champ {field_name} ne peut pas être vide.", field_name)


def validate_min_length(value: str, min_length: int, field_name: str) -> None:
    """
    Validate that a string has a minimum length.
    
    Args:
        value: The string to validate.
        min_length: The minimum length.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is shorter than the minimum length.
    """
    if len(value) < min_length:
        raise ValidationError(
            f"Le champ {field_name} doit contenir au moins {min_length} caractères.",
            field_name
        )


def validate_max_length(value: str, max_length: int, field_name: str) -> None:
    """
    Validate that a string has a maximum length.
    
    Args:
        value: The string to validate.
        max_length: The maximum length.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is longer than the maximum length.
    """
    if len(value) > max_length:
        raise ValidationError(
            f"Le champ {field_name} ne peut pas contenir plus de {max_length} caractères.",
            field_name
        )


def validate_min_value(value: Union[int, float], min_value: Union[int, float], field_name: str) -> None:
    """
    Validate that a number is greater than or equal to a minimum value.
    
    Args:
        value: The number to validate.
        min_value: The minimum value.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the number is less than the minimum value.
    """
    if value < min_value:
        raise ValidationError(
            f"Le champ {field_name} doit être supérieur ou égal à {min_value}.",
            field_name
        )


def validate_max_value(value: Union[int, float], max_value: Union[int, float], field_name: str) -> None:
    """
    Validate that a number is less than or equal to a maximum value.
    
    Args:
        value: The number to validate.
        max_value: The maximum value.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the number is greater than the maximum value.
    """
    if value > max_value:
        raise ValidationError(
            f"Le champ {field_name} doit être inférieur ou égal à {max_value}.",
            field_name
        )


def validate_pattern(value: str, pattern: Union[str, Pattern], field_name: str) -> None:
    """
    Validate that a string matches a pattern.
    
    Args:
        value: The string to validate.
        pattern: The pattern to match.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string does not match the pattern.
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    
    if not pattern.match(value):
        raise ValidationError(
            f"Le champ {field_name} ne correspond pas au format attendu.",
            field_name
        )


def validate_email_field(value: str, field_name: str) -> None:
    """
    Validate that a string is a valid email address.
    
    Args:
        value: The string to validate.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is not a valid email address.
    """
    if not validate_email(value):
        raise ValidationError(
            f"Le champ {field_name} doit être une adresse email valide.",
            field_name
        )


def validate_phone_field(value: str, field_name: str) -> None:
    """
    Validate that a string is a valid phone number.
    
    Args:
        value: The string to validate.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is not a valid phone number.
    """
    if not validate_phone(value):
        raise ValidationError(
            f"Le champ {field_name} doit être un numéro de téléphone valide.",
            field_name
        )


def validate_url_field(value: str, field_name: str) -> None:
    """
    Validate that a string is a valid URL.
    
    Args:
        value: The string to validate.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is not a valid URL.
    """
    if not validate_url(value):
        raise ValidationError(
            f"Le champ {field_name} doit être une URL valide.",
            field_name
        )


def validate_date_field(value: str, format: str, field_name: str) -> None:
    """
    Validate that a string is a valid date.
    
    Args:
        value: The string to validate.
        format: The expected date format.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is not a valid date.
    """
    if not validate_date(value, format):
        raise ValidationError(
            f"Le champ {field_name} doit être une date valide au format {format}.",
            field_name
        )


def validate_time_field(value: str, format: str, field_name: str) -> None:
    """
    Validate that a string is a valid time.
    
    Args:
        value: The string to validate.
        format: The expected time format.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is not a valid time.
    """
    if not validate_time(value, format):
        raise ValidationError(
            f"Le champ {field_name} doit être une heure valide au format {format}.",
            field_name
        )


def validate_datetime_field(value: str, format: str, field_name: str) -> None:
    """
    Validate that a string is a valid datetime.
    
    Args:
        value: The string to validate.
        format: The expected datetime format.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is not a valid datetime.
    """
    if not validate_datetime(value, format):
        raise ValidationError(
            f"Le champ {field_name} doit être une date et heure valide au format {format}.",
            field_name
        )


def validate_credit_card_field(value: str, field_name: str) -> None:
    """
    Validate that a string is a valid credit card number.
    
    Args:
        value: The string to validate.
        field_name: The name of the field being validated.
    
    Raises:
        ValidationError: If the string is not a valid credit card number.
    """
    if not validate_credit_card(value):
        raise ValidationError(
            f"Le champ {field_name} doit être un numéro de carte de crédit valide.",
            field_name
        )


def validate_password_field(
    value: str,
    field_name: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = True
) -> None:
    """
    Validate that a string is a strong password.
    
    Args:
        value: The string to validate.
        field_name: The name of the field being validated.
        min_length: Minimum password length.
        require_uppercase: Whether to require at least one uppercase letter.
        require_lowercase: Whether to require at least one lowercase letter.
        require_digit: Whether to require at least one digit.
        require_special: Whether to require at least one special character.
    
    Raises:
        ValidationError: If the string is not a strong password.
    """
    if not validate_password_strength(
        value,
        min_length,
        require_uppercase,
        require_lowercase,
        require_digit,
        require_special
    ):
        message = f"Le champ {field_name} doit contenir au moins {min_length} caractères"
        
        if require_uppercase:
            message += ", une lettre majuscule"
        
        if require_lowercase:
            message += ", une lettre minuscule"
        
        if require_digit:
            message += ", un chiffre"
        
        if require_special:
            message += ", un caractère spécial"
        
        message += "."
        
        raise ValidationError(message, field_name)

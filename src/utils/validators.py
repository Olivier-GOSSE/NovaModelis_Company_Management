"""
Validators utility module.
This module provides utilities for validating user input.
"""
import re
import logging
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, TypeVar, Union, cast

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class Validator:
    """Base validator class."""
    def __init__(self, message: Optional[str] = None):
        self.message = message
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate the value.
        
        Args:
            value: The value to validate.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        raise NotImplementedError("Subclasses must implement __call__")


class RequiredValidator(Validator):
    """Validator that checks if a value is not None or empty."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or "Ce champ est requis")
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return False, self.message
        
        if isinstance(value, str) and not value.strip():
            return False, self.message
        
        if isinstance(value, (list, dict, tuple)) and not value:
            return False, self.message
        
        return True, None


class MinLengthValidator(Validator):
    """Validator that checks if a string has a minimum length."""
    def __init__(self, min_length: int, message: Optional[str] = None):
        super().__init__(message or f"Ce champ doit contenir au moins {min_length} caractères")
        self.min_length = min_length
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None  # Skip validation if value is None
        
        if not isinstance(value, str):
            return False, "La valeur doit être une chaîne de caractères"
        
        if len(value) < self.min_length:
            return False, self.message
        
        return True, None


class MaxLengthValidator(Validator):
    """Validator that checks if a string has a maximum length."""
    def __init__(self, max_length: int, message: Optional[str] = None):
        super().__init__(message or f"Ce champ doit contenir au plus {max_length} caractères")
        self.max_length = max_length
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None  # Skip validation if value is None
        
        if not isinstance(value, str):
            return False, "La valeur doit être une chaîne de caractères"
        
        if len(value) > self.max_length:
            return False, self.message
        
        return True, None


class RegexValidator(Validator):
    """Validator that checks if a string matches a regular expression."""
    def __init__(self, pattern: Union[str, Pattern], message: Optional[str] = None):
        super().__init__(message or "Ce champ ne correspond pas au format attendu")
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None  # Skip validation if value is None
        
        if not isinstance(value, str):
            return False, "La valeur doit être une chaîne de caractères"
        
        if not self.pattern.match(value):
            return False, self.message
        
        return True, None


class EmailValidator(RegexValidator):
    """Validator that checks if a string is a valid email address."""
    def __init__(self, message: Optional[str] = None):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(pattern, message or "Adresse email invalide")


class PhoneValidator(RegexValidator):
    """Validator that checks if a string is a valid phone number."""
    def __init__(self, message: Optional[str] = None):
        # This is a simple pattern for international phone numbers
        # In a real application, you might want to use a more sophisticated library
        pattern = r'^\+?[0-9]{10,15}$'
        super().__init__(pattern, message or "Numéro de téléphone invalide")


class MinValueValidator(Validator):
    """Validator that checks if a number is greater than or equal to a minimum value."""
    def __init__(self, min_value: Union[int, float], message: Optional[str] = None):
        super().__init__(message or f"Ce champ doit être supérieur ou égal à {min_value}")
        self.min_value = min_value
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None  # Skip validation if value is None
        
        try:
            value_float = float(value)
        except (ValueError, TypeError):
            return False, "La valeur doit être un nombre"
        
        if value_float < self.min_value:
            return False, self.message
        
        return True, None


class MaxValueValidator(Validator):
    """Validator that checks if a number is less than or equal to a maximum value."""
    def __init__(self, max_value: Union[int, float], message: Optional[str] = None):
        super().__init__(message or f"Ce champ doit être inférieur ou égal à {max_value}")
        self.max_value = max_value
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None  # Skip validation if value is None
        
        try:
            value_float = float(value)
        except (ValueError, TypeError):
            return False, "La valeur doit être un nombre"
        
        if value_float > self.max_value:
            return False, self.message
        
        return True, None


class ChoiceValidator(Validator):
    """Validator that checks if a value is in a list of choices."""
    def __init__(self, choices: List[Any], message: Optional[str] = None):
        super().__init__(message or "Valeur non autorisée")
        self.choices = choices
    
    def __call__(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None  # Skip validation if value is None
        
        if value not in self.choices:
            return False, self.message
        
        return True, None


def validate_data(data: Dict[str, Any], validators: Dict[str, List[Validator]]) -> Dict[str, List[str]]:
    """
    Validate a dictionary of data against a dictionary of validators.
    
    Args:
        data: Dictionary of data to validate.
        validators: Dictionary of validators for each field.
    
    Returns:
        Dictionary of error messages for each field.
    """
    errors: Dict[str, List[str]] = {}
    
    for field, field_validators in validators.items():
        field_errors: List[str] = []
        value = data.get(field)
        
        for validator in field_validators:
            is_valid, error = validator(value)
            if not is_valid and error:
                field_errors.append(error)
        
        if field_errors:
            errors[field] = field_errors
    
    return errors


def is_valid(data: Dict[str, Any], validators: Dict[str, List[Validator]]) -> bool:
    """
    Check if a dictionary of data is valid against a dictionary of validators.
    
    Args:
        data: Dictionary of data to validate.
        validators: Dictionary of validators for each field.
    
    Returns:
        True if all fields are valid, False otherwise.
    """
    errors = validate_data(data, validators)
    return len(errors) == 0

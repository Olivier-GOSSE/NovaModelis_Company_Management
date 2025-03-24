"""
Utilitaires de validation pour l'application.
"""
import re
import datetime
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic

# Type générique pour les valeurs validées
T = TypeVar('T')

class ValidationError(Exception):
    """Exception levée lorsqu'une validation échoue."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)

class ValidationResult(Generic[T]):
    """Résultat d'une validation."""
    def __init__(self, is_valid: bool, value: Optional[T] = None, errors: Optional[Dict[str, str]] = None):
        self.is_valid = is_valid
        self.value = value
        self.errors = errors or {}
    
    def __bool__(self) -> bool:
        return self.is_valid

def validate_email(email: str) -> ValidationResult[str]:
    """
    Valider une adresse e-mail.
    
    Args:
        email: L'adresse e-mail à valider.
        
    Returns:
        Un résultat de validation.
    """
    if not email:
        return ValidationResult(False, None, {"email": "L'adresse e-mail est requise."})
    
    # Expression régulière pour valider les adresses e-mail
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return ValidationResult(False, None, {"email": "L'adresse e-mail n'est pas valide."})
    
    return ValidationResult(True, email)

def validate_phone(phone: str) -> ValidationResult[str]:
    """
    Valider un numéro de téléphone.
    
    Args:
        phone: Le numéro de téléphone à valider.
        
    Returns:
        Un résultat de validation.
    """
    if not phone:
        return ValidationResult(False, None, {"phone": "Le numéro de téléphone est requis."})
    
    # Supprimer les espaces, tirets, parenthèses, etc.
    cleaned_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Vérifier que le numéro ne contient que des chiffres
    if not cleaned_phone.isdigit():
        return ValidationResult(False, None, {"phone": "Le numéro de téléphone ne doit contenir que des chiffres."})
    
    # Vérifier la longueur (entre 8 et 15 chiffres)
    if len(cleaned_phone) < 8 or len(cleaned_phone) > 15:
        return ValidationResult(False, None, {"phone": "Le numéro de téléphone doit contenir entre 8 et 15 chiffres."})
    
    # Formater le numéro (exemple: +33 6 12 34 56 78)
    if cleaned_phone.startswith('33') and len(cleaned_phone) == 11:
        formatted_phone = '+33 ' + ' '.join([cleaned_phone[2:4], cleaned_phone[4:6], cleaned_phone[6:8], cleaned_phone[8:10], cleaned_phone[10:]])
    elif cleaned_phone.startswith('0') and len(cleaned_phone) == 10:
        formatted_phone = '+33 ' + ' '.join([cleaned_phone[1:3], cleaned_phone[3:5], cleaned_phone[5:7], cleaned_phone[7:9], cleaned_phone[9:]])
    else:
        formatted_phone = cleaned_phone
    
    return ValidationResult(True, formatted_phone)

def validate_date(date_str: str, format_str: str = '%Y-%m-%d') -> ValidationResult[datetime.date]:
    """
    Valider une date.
    
    Args:
        date_str: La date à valider sous forme de chaîne.
        format_str: Le format de la date.
        
    Returns:
        Un résultat de validation.
    """
    if not date_str:
        return ValidationResult(False, None, {"date": "La date est requise."})
    
    try:
        date_obj = datetime.datetime.strptime(date_str, format_str).date()
        return ValidationResult(True, date_obj)
    except ValueError:
        return ValidationResult(False, None, {"date": f"La date n'est pas au format {format_str}."})

def validate_required(value: Any, field_name: str) -> ValidationResult[Any]:
    """
    Valider qu'une valeur est présente.
    
    Args:
        value: La valeur à valider.
        field_name: Le nom du champ.
        
    Returns:
        Un résultat de validation.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return ValidationResult(False, None, {field_name: "Ce champ est requis."})
    
    return ValidationResult(True, value)

def validate_length(value: str, min_length: int = 0, max_length: Optional[int] = None, field_name: str = "value") -> ValidationResult[str]:
    """
    Valider la longueur d'une chaîne.
    
    Args:
        value: La chaîne à valider.
        min_length: La longueur minimale.
        max_length: La longueur maximale.
        field_name: Le nom du champ.
        
    Returns:
        Un résultat de validation.
    """
    if not isinstance(value, str):
        return ValidationResult(False, None, {field_name: "La valeur doit être une chaîne de caractères."})
    
    if len(value) < min_length:
        return ValidationResult(False, None, {field_name: f"Ce champ doit contenir au moins {min_length} caractères."})
    
    if max_length is not None and len(value) > max_length:
        return ValidationResult(False, None, {field_name: f"Ce champ ne doit pas dépasser {max_length} caractères."})
    
    return ValidationResult(True, value)

def validate_numeric(value: str, field_name: str = "value") -> ValidationResult[float]:
    """
    Valider qu'une chaîne représente un nombre.
    
    Args:
        value: La chaîne à valider.
        field_name: Le nom du champ.
        
    Returns:
        Un résultat de validation.
    """
    if not value:
        return ValidationResult(False, None, {field_name: "Ce champ est requis."})
    
    try:
        numeric_value = float(value)
        return ValidationResult(True, numeric_value)
    except ValueError:
        return ValidationResult(False, None, {field_name: "Ce champ doit être un nombre."})

def validate_integer(value: str, field_name: str = "value") -> ValidationResult[int]:
    """
    Valider qu'une chaîne représente un entier.
    
    Args:
        value: La chaîne à valider.
        field_name: Le nom du champ.
        
    Returns:
        Un résultat de validation.
    """
    if not value:
        return ValidationResult(False, None, {field_name: "Ce champ est requis."})
    
    try:
        int_value = int(value)
        return ValidationResult(True, int_value)
    except ValueError:
        return ValidationResult(False, None, {field_name: "Ce champ doit être un nombre entier."})

def validate_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                  max_value: Optional[Union[int, float]] = None, field_name: str = "value") -> ValidationResult[Union[int, float]]:
    """
    Valider qu'un nombre est dans une plage donnée.
    
    Args:
        value: Le nombre à valider.
        min_value: La valeur minimale.
        max_value: La valeur maximale.
        field_name: Le nom du champ.
        
    Returns:
        Un résultat de validation.
    """
    if not isinstance(value, (int, float)):
        return ValidationResult(False, None, {field_name: "La valeur doit être un nombre."})
    
    if min_value is not None and value < min_value:
        return ValidationResult(False, None, {field_name: f"Ce champ doit être supérieur ou égal à {min_value}."})
    
    if max_value is not None and value > max_value:
        return ValidationResult(False, None, {field_name: f"Ce champ doit être inférieur ou égal à {max_value}."})
    
    return ValidationResult(True, value)

def validate_regex(value: str, pattern: str, message: str, field_name: str = "value") -> ValidationResult[str]:
    """
    Valider qu'une chaîne correspond à une expression régulière.
    
    Args:
        value: La chaîne à valider.
        pattern: L'expression régulière.
        message: Le message d'erreur.
        field_name: Le nom du champ.
        
    Returns:
        Un résultat de validation.
    """
    if not isinstance(value, str):
        return ValidationResult(False, None, {field_name: "La valeur doit être une chaîne de caractères."})
    
    if not re.match(pattern, value):
        return ValidationResult(False, None, {field_name: message})
    
    return ValidationResult(True, value)

def validate_choice(value: Any, choices: List[Any], field_name: str = "value") -> ValidationResult[Any]:
    """
    Valider qu'une valeur fait partie d'une liste de choix.
    
    Args:
        value: La valeur à valider.
        choices: La liste des choix valides.
        field_name: Le nom du champ.
        
    Returns:
        Un résultat de validation.
    """
    if value not in choices:
        return ValidationResult(False, None, {field_name: "Cette valeur n'est pas valide."})
    
    return ValidationResult(True, value)

def validate_url(url: str) -> ValidationResult[str]:
    """
    Valider une URL.
    
    Args:
        url: L'URL à valider.
        
    Returns:
        Un résultat de validation.
    """
    if not url:
        return ValidationResult(False, None, {"url": "L'URL est requise."})
    
    # Expression régulière pour valider les URL
    pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
    
    if not re.match(pattern, url):
        return ValidationResult(False, None, {"url": "L'URL n'est pas valide."})
    
    # Ajouter le protocole si absent
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return ValidationResult(True, url)

def validate_postal_code(postal_code: str, country: str = 'FR') -> ValidationResult[str]:
    """
    Valider un code postal.
    
    Args:
        postal_code: Le code postal à valider.
        country: Le code du pays (ISO 3166-1 alpha-2).
        
    Returns:
        Un résultat de validation.
    """
    if not postal_code:
        return ValidationResult(False, None, {"postal_code": "Le code postal est requis."})
    
    # Patterns par pays
    patterns = {
        'FR': r'^\d{5}$',  # France: 5 chiffres
        'BE': r'^\d{4}$',  # Belgique: 4 chiffres
        'CH': r'^\d{4}$',  # Suisse: 4 chiffres
        'CA': r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$',  # Canada: A1A 1A1
        'US': r'^\d{5}(-\d{4})?$',  # États-Unis: 5 chiffres ou 5+4
        'UK': r'^[A-Za-z]{1,2}\d{1,2}[A-Za-z]? \d[A-Za-z]{2}$'  # Royaume-Uni: AA1A 1AA
    }
    
    # Utiliser le pattern par défaut si le pays n'est pas dans la liste
    pattern = patterns.get(country.upper(), r'^\d{4,10}$')
    
    if not re.match(pattern, postal_code):
        return ValidationResult(False, None, {"postal_code": "Le code postal n'est pas valide pour ce pays."})
    
    return ValidationResult(True, postal_code)

def validate_form(data: Dict[str, Any], validators: Dict[str, Callable[[Any], ValidationResult]]) -> ValidationResult[Dict[str, Any]]:
    """
    Valider un formulaire complet.
    
    Args:
        data: Les données du formulaire.
        validators: Les validateurs à appliquer pour chaque champ.
        
    Returns:
        Un résultat de validation.
    """
    validated_data = {}
    errors = {}
    
    for field, validator in validators.items():
        field_value = data.get(field)
        result = validator(field_value)
        
        if result.is_valid:
            validated_data[field] = result.value
        else:
            errors.update(result.errors)
    
    if errors:
        return ValidationResult(False, None, errors)
    
    return ValidationResult(True, validated_data)

def validate_password_strength(password: str) -> ValidationResult[str]:
    """
    Valider la force d'un mot de passe.
    
    Args:
        password: Le mot de passe à valider.
        
    Returns:
        Un résultat de validation.
    """
    if not password:
        return ValidationResult(False, None, {"password": "Le mot de passe est requis."})
    
    # Vérifier la longueur
    if len(password) < 8:
        return ValidationResult(False, None, {"password": "Le mot de passe doit contenir au moins 8 caractères."})
    
    # Vérifier la présence de lettres minuscules
    if not re.search(r'[a-z]', password):
        return ValidationResult(False, None, {"password": "Le mot de passe doit contenir au moins une lettre minuscule."})
    
    # Vérifier la présence de lettres majuscules
    if not re.search(r'[A-Z]', password):
        return ValidationResult(False, None, {"password": "Le mot de passe doit contenir au moins une lettre majuscule."})
    
    # Vérifier la présence de chiffres
    if not re.search(r'\d', password):
        return ValidationResult(False, None, {"password": "Le mot de passe doit contenir au moins un chiffre."})
    
    # Vérifier la présence de caractères spéciaux
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return ValidationResult(False, None, {"password": "Le mot de passe doit contenir au moins un caractère spécial."})
    
    return ValidationResult(True, password)

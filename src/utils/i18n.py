"""
Internationalization utility module.
This module provides utilities for internationalization and localization.
"""
import os
import json
import logging
import locale
from typing import Any, Dict, List, Optional, Union, cast

logger = logging.getLogger(__name__)

# Type aliases
TranslationDict = Dict[str, Dict[str, str]]
LocaleDict = Dict[str, Any]

# Global variables
_translations: TranslationDict = {}
_current_language: str = "fr"  # Default language
_fallback_language: str = "fr"  # Fallback language
_locale_data: Dict[str, LocaleDict] = {}


def load_translations(translations_dir: str) -> None:
    """
    Load translations from JSON files in the specified directory.
    
    Args:
        translations_dir: Directory containing translation files.
            Each file should be named with the language code (e.g., fr.json, en.json).
    """
    global _translations
    
    if not os.path.isdir(translations_dir):
        logger.error(f"Translations directory not found: {translations_dir}")
        return
    
    # Clear existing translations
    _translations = {}
    
    # Load translation files
    for filename in os.listdir(translations_dir):
        if not filename.endswith(".json"):
            continue
        
        language_code = os.path.splitext(filename)[0]
        file_path = os.path.join(translations_dir, filename)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations = json.load(f)
                
                if not isinstance(translations, dict):
                    logger.error(f"Invalid translation file format: {file_path}")
                    continue
                
                _translations[language_code] = translations
                logger.info(f"Loaded translations for {language_code}")
        except Exception as e:
            logger.error(f"Error loading translation file {file_path}: {str(e)}")
    
    logger.info(f"Loaded translations for {len(_translations)} languages")


def set_language(language_code: str) -> bool:
    """
    Set the current language.
    
    Args:
        language_code: Language code (e.g., "fr", "en").
    
    Returns:
        True if the language was set successfully, False otherwise.
    """
    global _current_language
    
    if language_code not in _translations:
        logger.warning(f"Language {language_code} not available, using fallback language {_fallback_language}")
        return False
    
    _current_language = language_code
    logger.info(f"Language set to {language_code}")
    
    # Set locale for date and number formatting
    try:
        locale.setlocale(locale.LC_ALL, _locale_data.get(language_code, {}).get("locale_code", ""))
        logger.debug(f"Locale set to {locale.getlocale()}")
    except locale.Error as e:
        logger.warning(f"Error setting locale for {language_code}: {str(e)}")
    
    return True


def get_current_language() -> str:
    """
    Get the current language code.
    
    Returns:
        Current language code.
    """
    return _current_language


def get_available_languages() -> List[str]:
    """
    Get a list of available language codes.
    
    Returns:
        List of available language codes.
    """
    return list(_translations.keys())


def translate(key: str, default: Optional[str] = None, **kwargs: Any) -> str:
    """
    Translate a key to the current language.
    
    Args:
        key: Translation key.
        default: Default value if the key is not found.
        **kwargs: Format arguments for the translated string.
    
    Returns:
        Translated string.
    """
    # Try to get the translation in the current language
    translation = _translations.get(_current_language, {}).get(key)
    
    # If not found, try the fallback language
    if translation is None and _fallback_language != _current_language:
        translation = _translations.get(_fallback_language, {}).get(key)
    
    # If still not found, use the default or the key itself
    if translation is None:
        translation = default if default is not None else key
    
    # Format the translation with the provided arguments
    if kwargs:
        try:
            return translation.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing format argument in translation '{key}': {str(e)}")
            return translation
        except Exception as e:
            logger.warning(f"Error formatting translation '{key}': {str(e)}")
            return translation
    
    return translation


def setup_locale_data() -> None:
    """
    Set up locale data for supported languages.
    """
    global _locale_data
    
    _locale_data = {
        "fr": {
            "name": "Français",
            "locale_code": "fr_FR.UTF-8",
            "date_format": "%d/%m/%Y",
            "time_format": "%H:%M:%S",
            "datetime_format": "%d/%m/%Y %H:%M:%S",
            "decimal_separator": ",",
            "thousands_separator": " ",
            "currency_symbol": "€",
            "currency_code": "EUR",
            "currency_format": "{value} {symbol}",
        },
        "en": {
            "name": "English",
            "locale_code": "en_US.UTF-8",
            "date_format": "%m/%d/%Y",
            "time_format": "%I:%M:%S %p",
            "datetime_format": "%m/%d/%Y %I:%M:%S %p",
            "decimal_separator": ".",
            "thousands_separator": ",",
            "currency_symbol": "$",
            "currency_code": "USD",
            "currency_format": "{symbol}{value}",
        },
    }


def get_locale_data(language_code: Optional[str] = None) -> LocaleDict:
    """
    Get locale data for a language.
    
    Args:
        language_code: Language code. If None, uses the current language.
    
    Returns:
        Locale data dictionary.
    """
    if language_code is None:
        language_code = _current_language
    
    return _locale_data.get(language_code, _locale_data.get(_fallback_language, {}))


def format_date(date: Any, format_str: Optional[str] = None, language_code: Optional[str] = None) -> str:
    """
    Format a date according to the locale.
    
    Args:
        date: Date to format (datetime.date or datetime.datetime).
        format_str: Format string. If None, uses the locale's date format.
        language_code: Language code. If None, uses the current language.
    
    Returns:
        Formatted date string.
    """
    if language_code is None:
        language_code = _current_language
    
    locale_data = get_locale_data(language_code)
    
    if format_str is None:
        format_str = locale_data.get("date_format", "%d/%m/%Y")
    
    try:
        return date.strftime(format_str)
    except Exception as e:
        logger.warning(f"Error formatting date: {str(e)}")
        return str(date)


def format_time(time: Any, format_str: Optional[str] = None, language_code: Optional[str] = None) -> str:
    """
    Format a time according to the locale.
    
    Args:
        time: Time to format (datetime.time or datetime.datetime).
        format_str: Format string. If None, uses the locale's time format.
        language_code: Language code. If None, uses the current language.
    
    Returns:
        Formatted time string.
    """
    if language_code is None:
        language_code = _current_language
    
    locale_data = get_locale_data(language_code)
    
    if format_str is None:
        format_str = locale_data.get("time_format", "%H:%M:%S")
    
    try:
        return time.strftime(format_str)
    except Exception as e:
        logger.warning(f"Error formatting time: {str(e)}")
        return str(time)


def format_datetime(dt: Any, format_str: Optional[str] = None, language_code: Optional[str] = None) -> str:
    """
    Format a datetime according to the locale.
    
    Args:
        dt: Datetime to format (datetime.datetime).
        format_str: Format string. If None, uses the locale's datetime format.
        language_code: Language code. If None, uses the current language.
    
    Returns:
        Formatted datetime string.
    """
    if language_code is None:
        language_code = _current_language
    
    locale_data = get_locale_data(language_code)
    
    if format_str is None:
        format_str = locale_data.get("datetime_format", "%d/%m/%Y %H:%M:%S")
    
    try:
        return dt.strftime(format_str)
    except Exception as e:
        logger.warning(f"Error formatting datetime: {str(e)}")
        return str(dt)


def format_number(
    value: Union[int, float],
    decimal_places: Optional[int] = None,
    language_code: Optional[str] = None
) -> str:
    """
    Format a number according to the locale.
    
    Args:
        value: Number to format.
        decimal_places: Number of decimal places. If None, uses all decimal places.
        language_code: Language code. If None, uses the current language.
    
    Returns:
        Formatted number string.
    """
    if language_code is None:
        language_code = _current_language
    
    locale_data = get_locale_data(language_code)
    
    decimal_separator = locale_data.get("decimal_separator", ".")
    thousands_separator = locale_data.get("thousands_separator", ",")
    
    try:
        # Format the number
        if decimal_places is not None:
            value_str = f"{value:.{decimal_places}f}"
        else:
            value_str = str(value)
        
        # Split into integer and decimal parts
        if "." in value_str:
            integer_part, decimal_part = value_str.split(".")
        else:
            integer_part, decimal_part = value_str, ""
        
        # Add thousands separator
        integer_part = "".join(
            c + (thousands_separator if i > 0 and i % 3 == 0 else "")
            for i, c in enumerate(reversed(integer_part))
        )
        integer_part = "".join(reversed(integer_part))
        
        # Combine parts with decimal separator
        if decimal_part:
            return f"{integer_part}{decimal_separator}{decimal_part}"
        else:
            return integer_part
    except Exception as e:
        logger.warning(f"Error formatting number: {str(e)}")
        return str(value)


def format_currency(
    value: Union[int, float],
    decimal_places: int = 2,
    language_code: Optional[str] = None
) -> str:
    """
    Format a currency value according to the locale.
    
    Args:
        value: Currency value to format.
        decimal_places: Number of decimal places.
        language_code: Language code. If None, uses the current language.
    
    Returns:
        Formatted currency string.
    """
    if language_code is None:
        language_code = _current_language
    
    locale_data = get_locale_data(language_code)
    
    currency_symbol = locale_data.get("currency_symbol", "€")
    currency_format = locale_data.get("currency_format", "{value} {symbol}")
    
    # Format the number
    formatted_value = format_number(value, decimal_places, language_code)
    
    # Apply the currency format
    return currency_format.format(value=formatted_value, symbol=currency_symbol)


# Initialize locale data
setup_locale_data()

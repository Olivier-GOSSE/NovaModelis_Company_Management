"""
Module for handling currencies in the application.
"""
import os
import json
import logging

# Default currency
DEFAULT_CURRENCY = "EUR"  # Euro as default

# Available currencies
AVAILABLE_CURRENCIES = {
    "EUR": {
        "symbol": "€",
        "name": "Euro",
        "position": "after",  # Symbol position: "before" or "after" the amount
        "decimal_separator": ",",
        "thousands_separator": " ",
        "decimal_places": 2
    },
    "USD": {
        "symbol": "$",
        "name": "US Dollar",
        "position": "before",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "decimal_places": 2
    },
    "GBP": {
        "symbol": "£",
        "name": "British Pound",
        "position": "before",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "decimal_places": 2
    },
    "CAD": {
        "symbol": "CA$",
        "name": "Canadian Dollar",
        "position": "before",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "decimal_places": 2
    },
    "CHF": {
        "symbol": "CHF",
        "name": "Swiss Franc",
        "position": "after",
        "decimal_separator": ".",
        "thousands_separator": "'",
        "decimal_places": 2
    },
    "JPY": {
        "symbol": "¥",
        "name": "Japanese Yen",
        "position": "before",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "decimal_places": 0
    }
}

# Current currency
_current_currency = DEFAULT_CURRENCY

def set_currency(currency_code):
    """
    Set the current currency.
    
    Args:
        currency_code (str): The currency code to set.
    
    Returns:
        bool: True if the currency was set successfully, False otherwise.
    """
    global _current_currency
    
    if currency_code in AVAILABLE_CURRENCIES:
        _current_currency = currency_code
        logging.info(f"Currency set to {currency_code}")
        return True
    else:
        logging.warning(f"Unsupported currency: {currency_code}")
        return False

def get_current_currency():
    """
    Get the current currency code.
    
    Returns:
        str: The current currency code.
    """
    return _current_currency

def get_currency_info(currency_code=None):
    """
    Get information about a currency.
    
    Args:
        currency_code (str, optional): The currency code. Defaults to the current currency.
    
    Returns:
        dict: The currency information.
    """
    code = currency_code or _current_currency
    return AVAILABLE_CURRENCIES.get(code, AVAILABLE_CURRENCIES[DEFAULT_CURRENCY])

def format_currency(amount, currency_code=None):
    """
    Format an amount with the current currency symbol.
    
    Args:
        amount (float): The amount to format.
        currency_code (str, optional): The currency code. Defaults to the current currency.
    
    Returns:
        str: The formatted amount with currency symbol.
    """
    currency = get_currency_info(currency_code)
    
    # Format the number with the appropriate decimal and thousands separators
    formatted_number = format_number(
        amount, 
        currency["decimal_places"], 
        currency["decimal_separator"], 
        currency["thousands_separator"]
    )
    
    # Add the currency symbol in the correct position
    if currency["position"] == "before":
        return f"{currency['symbol']}{formatted_number}"
    else:
        return f"{formatted_number} {currency['symbol']}"

def format_number(number, decimal_places, decimal_separator, thousands_separator):
    """
    Format a number with the specified decimal and thousands separators.
    
    Args:
        number (float): The number to format.
        decimal_places (int): The number of decimal places.
        decimal_separator (str): The decimal separator.
        thousands_separator (str): The thousands separator.
    
    Returns:
        str: The formatted number.
    """
    # Round the number to the specified decimal places
    rounded = round(number, decimal_places)
    
    # Split the number into integer and decimal parts
    if decimal_places > 0:
        integer_part, decimal_part = str(rounded).split('.')
        # Pad the decimal part with zeros if necessary
        decimal_part = decimal_part.ljust(decimal_places, '0')
    else:
        integer_part = str(int(rounded))
        decimal_part = ""
    
    # Add thousands separators to the integer part
    if thousands_separator:
        formatted_integer = ""
        for i, digit in enumerate(str(int(number))[::-1]):
            if i > 0 and i % 3 == 0:
                formatted_integer = thousands_separator + formatted_integer
            formatted_integer = digit + formatted_integer
        integer_part = formatted_integer
    
    # Combine the integer and decimal parts with the decimal separator
    if decimal_places > 0:
        return f"{integer_part}{decimal_separator}{decimal_part}"
    else:
        return integer_part

def get_currency_display_name(currency_code=None):
    """
    Get the display name of a currency (symbol + name).
    
    Args:
        currency_code (str, optional): The currency code. Defaults to the current currency.
    
    Returns:
        str: The display name of the currency.
    """
    currency = get_currency_info(currency_code or _current_currency)
    return f"{currency['symbol']} ({currency['name']})"

def get_available_currencies_display():
    """
    Get a list of available currencies for display in UI.
    
    Returns:
        list: A list of tuples (code, display_name) for all available currencies.
    """
    return [(code, f"{info['symbol']} ({info['name']})") 
            for code, info in AVAILABLE_CURRENCIES.items()]

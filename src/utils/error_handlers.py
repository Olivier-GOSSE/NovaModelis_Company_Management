"""
Error handlers utility module.
This module provides utilities for handling errors in the application.
"""
import sys
import logging
import traceback
from types import TracebackType
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

from PySide6.QtWidgets import QMessageBox, QWidget

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')

class ApplicationError(Exception):
    """Base class for application errors."""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class DatabaseError(ApplicationError):
    """Error raised for database operations."""
    pass


class ValidationError(ApplicationError):
    """Error raised for validation errors."""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[str] = None):
        self.field = field
        super().__init__(message, details)


class NetworkError(ApplicationError):
    """Error raised for network operations."""
    pass


class ResourceError(ApplicationError):
    """Error raised for resource operations."""
    pass


class ConfigurationError(ApplicationError):
    """Error raised for configuration errors."""
    pass


class PermissionError(ApplicationError):
    """Error raised for permission errors."""
    pass


def handle_error(
    error: Exception,
    parent: Optional[QWidget] = None,
    show_message_box: bool = True,
    log_error: bool = True,
    reraise: bool = False
) -> None:
    """
    Handle an error by logging it and optionally showing a message box.
    
    Args:
        error: The error to handle.
        parent: The parent widget for the message box.
        show_message_box: Whether to show a message box.
        log_error: Whether to log the error.
        reraise: Whether to reraise the error after handling.
    """
    # Get error details
    error_type = type(error).__name__
    error_message = str(error)
    error_traceback = traceback.format_exc()
    
    # Log the error
    if log_error:
        logger.error(f"{error_type}: {error_message}")
        logger.debug(error_traceback)
    
    # Show a message box
    if show_message_box:
        title = "Erreur"
        message = error_message
        details = None
        
        # Customize based on error type
        if isinstance(error, DatabaseError):
            title = "Erreur de base de données"
            message = "Une erreur est survenue lors de l'accès à la base de données."
            details = error_message
        elif isinstance(error, ValidationError):
            title = "Erreur de validation"
            if error.field:
                message = f"Erreur de validation dans le champ '{error.field}': {error_message}"
            else:
                message = f"Erreur de validation: {error_message}"
            details = error.details
        elif isinstance(error, NetworkError):
            title = "Erreur réseau"
            message = "Une erreur réseau est survenue."
            details = error_message
        elif isinstance(error, ResourceError):
            title = "Erreur de ressource"
            message = "Une erreur est survenue lors de l'accès à une ressource."
            details = error_message
        elif isinstance(error, ConfigurationError):
            title = "Erreur de configuration"
            message = "Une erreur de configuration est survenue."
            details = error_message
        elif isinstance(error, PermissionError):
            title = "Erreur de permission"
            message = "Vous n'avez pas les permissions nécessaires pour effectuer cette action."
            details = error_message
        
        # Show the message box
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        
        if details:
            msg_box.setDetailedText(details)
        
        msg_box.exec()
    
    # Reraise the error if requested
    if reraise:
        raise error


def error_handler(
    show_message_box: bool = True,
    log_error: bool = True,
    reraise: bool = False
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for handling errors in functions.
    
    Args:
        show_message_box: Whether to show a message box.
        log_error: Whether to log the error.
        reraise: Whether to reraise the error after handling.
    
    Returns:
        Decorated function that handles errors.
    
    Example:
        @error_handler(show_message_box=True, log_error=True)
        def my_function():
            # Function that might raise an error
            pass
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        def wrapper(*args: Any, **kwargs: Any) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Find the parent widget if any
                parent = None
                for arg in args:
                    if isinstance(arg, QWidget):
                        parent = arg
                        break
                
                handle_error(
                    e,
                    parent=parent,
                    show_message_box=show_message_box,
                    log_error=log_error,
                    reraise=reraise
                )
                
                # Return a default value if not reraising
                if not reraise:
                    return cast(R, None)
                
                # This line is never reached if reraise is True
                raise
        
        return wrapper
    
    return decorator


def global_exception_handler(exctype: Type[BaseException], value: BaseException, tb: Optional[TracebackType]) -> None:
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        exctype: The exception type.
        value: The exception value.
        tb: The traceback.
    """
    # Log the error
    error_message = str(value)
    error_traceback = "".join(traceback.format_exception(exctype, value, tb))
    
    logger.critical(f"Unhandled exception: {error_message}")
    logger.critical(error_traceback)
    
    # Show a message box
    app = QWidget.instance()
    if app:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Erreur non gérée")
        msg_box.setText("Une erreur non gérée est survenue. L'application va se fermer.")
        msg_box.setDetailedText(error_traceback)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.exec()
    
    # Exit the application
    sys.exit(1)


def install_global_exception_handler() -> None:
    """
    Install the global exception handler.
    """
    sys.excepthook = global_exception_handler
    logger.info("Global exception handler installed")

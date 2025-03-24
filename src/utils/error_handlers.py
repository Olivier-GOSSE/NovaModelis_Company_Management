"""
Gestionnaires d'erreurs pour l'application.
"""
import sys
import logging
import traceback
from typing import Callable, Any, Optional, Dict, Type, List
from functools import wraps
from PySide6.QtWidgets import QMessageBox, QApplication

# Liste des erreurs connues et leurs messages utilisateur
ERROR_MESSAGES: Dict[Type[Exception], str] = {
    ConnectionError: "Impossible de se connecter à la base de données. Veuillez vérifier votre connexion réseau.",
    PermissionError: "Vous n'avez pas les permissions nécessaires pour effectuer cette action.",
    FileNotFoundError: "Le fichier demandé est introuvable.",
    ValueError: "Une valeur incorrecte a été fournie.",
    TypeError: "Type de données incorrect.",
    KeyError: "Clé non trouvée dans les données.",
    IndexError: "Index hors limites.",
    ZeroDivisionError: "Division par zéro détectée.",
    MemoryError: "Mémoire insuffisante pour effectuer l'opération.",
    TimeoutError: "L'opération a expiré. Veuillez réessayer."
}

class ApplicationError(Exception):
    """
    Classe de base pour les erreurs spécifiques à l'application.
    """
    def __init__(self, message: str, details: Optional[str] = None, error_code: Optional[int] = None):
        self.message = message
        self.details = details
        self.error_code = error_code
        super().__init__(message)

class DatabaseError(ApplicationError):
    """Erreur liée à la base de données."""
    pass

class ValidationError(ApplicationError):
    """Erreur de validation des données."""
    pass

class AuthenticationError(ApplicationError):
    """Erreur d'authentification."""
    pass

class ResourceError(ApplicationError):
    """Erreur liée aux ressources (fichiers, images, etc.)."""
    pass

class NetworkError(ApplicationError):
    """Erreur réseau."""
    pass

def handle_exceptions(func: Callable) -> Callable:
    """
    Décorateur pour gérer les exceptions et afficher un message d'erreur approprié.
    
    Args:
        func: La fonction à décorer.
        
    Returns:
        La fonction décorée.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Journaliser l'erreur
            logging.error(f"Erreur dans {func.__name__}: {str(e)}")
            logging.error(traceback.format_exc())
            
            # Déterminer le message d'erreur à afficher
            error_message = "Une erreur inattendue s'est produite."
            
            # Vérifier si c'est une erreur connue
            for error_type, message in ERROR_MESSAGES.items():
                if isinstance(e, error_type):
                    error_message = message
                    break
            
            # Si c'est une erreur d'application, utiliser son message
            if isinstance(e, ApplicationError):
                error_message = e.message
                if e.details:
                    error_message += f"\n\nDétails: {e.details}"
            
            # Afficher un message d'erreur à l'utilisateur
            app = QApplication.instance()
            if app:
                QMessageBox.critical(None, "Erreur", error_message)
            
            # Retourner None ou réessayer selon le contexte
            return None
    
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0, 
          exceptions: List[Type[Exception]] = None) -> Callable:
    """
    Décorateur pour réessayer une fonction en cas d'échec.
    
    Args:
        max_attempts: Nombre maximum de tentatives.
        delay: Délai entre les tentatives (en secondes).
        exceptions: Liste des exceptions à intercepter. Si None, toutes les exceptions sont interceptées.
        
    Returns:
        Le décorateur.
    """
    import time
    
    if exceptions is None:
        exceptions = [Exception]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as e:
                    last_exception = e
                    logging.warning(f"Tentative {attempt + 1}/{max_attempts} échouée pour {func.__name__}: {str(e)}")
                    
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            
            # Toutes les tentatives ont échoué
            logging.error(f"Toutes les tentatives ont échoué pour {func.__name__}: {str(last_exception)}")
            raise last_exception
        
        return wrapper
    
    return decorator

def log_exceptions(logger: Optional[logging.Logger] = None) -> Callable:
    """
    Décorateur pour journaliser les exceptions sans les intercepter.
    
    Args:
        logger: Logger à utiliser. Si None, le logger racine est utilisé.
        
    Returns:
        Le décorateur.
    """
    if logger is None:
        logger = logging.getLogger()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception dans {func.__name__}: {str(e)}")
                logger.error(traceback.format_exc())
                raise  # Relancer l'exception
        
        return wrapper
    
    return decorator

def global_exception_handler(exctype, value, tb):
    """
    Gestionnaire d'exceptions global pour l'application.
    
    Args:
        exctype: Type de l'exception.
        value: Valeur de l'exception.
        tb: Traceback de l'exception.
    """
    # Journaliser l'erreur
    logging.critical("Exception non gérée:")
    logging.critical(''.join(traceback.format_exception(exctype, value, tb)))
    
    # Afficher un message d'erreur à l'utilisateur
    app = QApplication.instance()
    if app:
        error_message = "Une erreur critique s'est produite. L'application va être fermée."
        
        # Ajouter des détails pour les erreurs connues
        for error_type, message in ERROR_MESSAGES.items():
            if issubclass(exctype, error_type):
                error_message = f"{message}\n\nL'application va être fermée."
                break
        
        QMessageBox.critical(None, "Erreur critique", error_message)
    
    # Appeler le gestionnaire d'exceptions par défaut
    sys.__excepthook__(exctype, value, tb)

def setup_exception_handling():
    """
    Configurer la gestion des exceptions pour l'application.
    """
    # Définir le gestionnaire d'exceptions global
    sys.excepthook = global_exception_handler
    
    # Configurer la journalisation des erreurs
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='data/logs/novamodelisapp.log',
        filemode='a'
    )
    
    logging.info("Gestionnaire d'exceptions configuré")

def safe_call(func: Callable, *args, default_value: Any = None, **kwargs) -> Any:
    """
    Appeler une fonction de manière sécurisée, en retournant une valeur par défaut en cas d'erreur.
    
    Args:
        func: La fonction à appeler.
        *args: Arguments positionnels pour la fonction.
        default_value: Valeur à retourner en cas d'erreur.
        **kwargs: Arguments nommés pour la fonction.
        
    Returns:
        Le résultat de la fonction ou la valeur par défaut en cas d'erreur.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Erreur lors de l'appel de {func.__name__}: {str(e)}")
        return default_value

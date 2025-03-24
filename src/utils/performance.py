"""
Utilitaires d'optimisation des performances pour l'application.
"""
import time
import functools
import logging
from typing import Callable, Any, Dict, Optional
import threading
from concurrent.futures import ThreadPoolExecutor

# Cache en mémoire simple
_memory_cache: Dict[str, Dict[str, Any]] = {
    "data": {},
    "expiry": {}
}
_cache_lock = threading.RLock()

def measure_time(func: Callable) -> Callable:
    """
    Décorateur pour mesurer le temps d'exécution d'une fonction.
    
    Args:
        func: La fonction à mesurer.
        
    Returns:
        La fonction décorée.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Calculer la durée en millisecondes
        duration = (end_time - start_time) * 1000
        
        # Journaliser la durée
        logging.debug(f"Performance: {func.__name__} a pris {duration:.2f} ms")
        
        return result
    
    return wrapper

def cache_result(expiry_seconds: int = 300) -> Callable:
    """
    Décorateur pour mettre en cache le résultat d'une fonction.
    
    Args:
        expiry_seconds: Durée de validité du cache en secondes.
        
    Returns:
        Le décorateur.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Créer une clé de cache basée sur la fonction et ses arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            with _cache_lock:
                # Vérifier si le résultat est dans le cache et n'a pas expiré
                current_time = time.time()
                if (cache_key in _memory_cache["data"] and 
                    _memory_cache["expiry"].get(cache_key, 0) > current_time):
                    return _memory_cache["data"][cache_key]
                
                # Exécuter la fonction et stocker le résultat
                result = func(*args, **kwargs)
                _memory_cache["data"][cache_key] = result
                _memory_cache["expiry"][cache_key] = current_time + expiry_seconds
                
                return result
        
        return wrapper
    
    return decorator

def clear_cache() -> None:
    """
    Vider le cache en mémoire.
    """
    with _cache_lock:
        _memory_cache["data"].clear()
        _memory_cache["expiry"].clear()
    logging.debug("Cache en mémoire vidé")

def run_in_thread(func: Callable) -> Callable:
    """
    Décorateur pour exécuter une fonction dans un thread séparé.
    
    Args:
        func: La fonction à exécuter dans un thread.
        
    Returns:
        La fonction décorée.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    
    return wrapper

class ThreadPool:
    """
    Gestionnaire de pool de threads pour exécuter des tâches en parallèle.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ThreadPool, cls).__new__(cls)
                cls._instance._executor = ThreadPoolExecutor(max_workers=10)
            return cls._instance
    
    def submit(self, func: Callable, *args, **kwargs):
        """
        Soumettre une tâche au pool de threads.
        
        Args:
            func: La fonction à exécuter.
            *args: Arguments positionnels pour la fonction.
            **kwargs: Arguments nommés pour la fonction.
            
        Returns:
            Un objet Future représentant l'exécution de la tâche.
        """
        return self._executor.submit(func, *args, **kwargs)
    
    def shutdown(self, wait: bool = True):
        """
        Arrêter le pool de threads.
        
        Args:
            wait: Si True, attendre que toutes les tâches soient terminées.
        """
        self._executor.shutdown(wait=wait)

def batch_process(items: list, process_func: Callable, batch_size: int = 100) -> list:
    """
    Traiter une liste d'éléments par lots pour améliorer les performances.
    
    Args:
        items: Liste d'éléments à traiter.
        process_func: Fonction de traitement à appliquer à chaque lot.
        batch_size: Taille de chaque lot.
        
    Returns:
        Liste des résultats combinés.
    """
    results = []
    
    # Traiter par lots
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = process_func(batch)
        results.extend(batch_results)
    
    return results

def lazy_property(func: Callable) -> property:
    """
    Décorateur pour créer une propriété calculée une seule fois et mise en cache.
    
    Args:
        func: La fonction à transformer en propriété paresseuse.
        
    Returns:
        Un descripteur de propriété.
    """
    attr_name = '_lazy_' + func.__name__
    
    @property
    @functools.wraps(func)
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    
    return _lazy_property

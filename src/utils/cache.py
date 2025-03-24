"""
Système de cache pour l'application.
"""
import time
import threading
import logging
import pickle
import os
import hashlib
from typing import Any, Dict, Optional, Callable, Tuple, List, Union, TypeVar

# Type générique pour les résultats de fonctions
T = TypeVar('T')

class Cache:
    """
    Classe de base pour les implémentations de cache.
    """
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Récupérer une valeur du cache.
        
        Args:
            key: La clé de la valeur à récupérer.
            
        Returns:
            Un tuple (hit, value) où hit est un booléen indiquant si la valeur a été trouvée
            et value est la valeur récupérée (ou None si hit est False).
        """
        raise NotImplementedError("La méthode get doit être implémentée par les sous-classes")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Définir une valeur dans le cache.
        
        Args:
            key: La clé sous laquelle stocker la valeur.
            value: La valeur à stocker.
            ttl: Durée de vie en secondes (None pour une durée illimitée).
        """
        raise NotImplementedError("La méthode set doit être implémentée par les sous-classes")
    
    def delete(self, key: str) -> bool:
        """
        Supprimer une valeur du cache.
        
        Args:
            key: La clé de la valeur à supprimer.
            
        Returns:
            True si la valeur a été supprimée, False sinon.
        """
        raise NotImplementedError("La méthode delete doit être implémentée par les sous-classes")
    
    def clear(self) -> None:
        """
        Vider le cache.
        """
        raise NotImplementedError("La méthode clear doit être implémentée par les sous-classes")
    
    def get_or_set(self, key: str, default_factory: Callable[[], T], ttl: Optional[int] = None) -> T:
        """
        Récupérer une valeur du cache ou la définir si elle n'existe pas.
        
        Args:
            key: La clé de la valeur à récupérer.
            default_factory: Fonction à appeler pour obtenir la valeur par défaut.
            ttl: Durée de vie en secondes (None pour une durée illimitée).
            
        Returns:
            La valeur récupérée ou définie.
        """
        hit, value = self.get(key)
        if hit:
            return value
        
        value = default_factory()
        self.set(key, value, ttl)
        return value

class MemoryCache(Cache):
    """
    Implémentation de cache en mémoire.
    """
    def __init__(self, default_ttl: Optional[int] = None):
        """
        Initialiser le cache en mémoire.
        
        Args:
            default_ttl: Durée de vie par défaut en secondes (None pour une durée illimitée).
        """
        self.default_ttl = default_ttl
        self.cache: Dict[str, Any] = {}
        self.expiry: Dict[str, float] = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Récupérer une valeur du cache.
        
        Args:
            key: La clé de la valeur à récupérer.
            
        Returns:
            Un tuple (hit, value) où hit est un booléen indiquant si la valeur a été trouvée
            et value est la valeur récupérée (ou None si hit est False).
        """
        with self.lock:
            # Vérifier si la clé existe
            if key not in self.cache:
                return False, None
            
            # Vérifier si la valeur a expiré
            if key in self.expiry and self.expiry[key] <= time.time():
                del self.cache[key]
                del self.expiry[key]
                return False, None
            
            return True, self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Définir une valeur dans le cache.
        
        Args:
            key: La clé sous laquelle stocker la valeur.
            value: La valeur à stocker.
            ttl: Durée de vie en secondes (None pour utiliser la durée par défaut).
        """
        with self.lock:
            self.cache[key] = value
            
            # Définir l'expiration si nécessaire
            if ttl is not None:
                self.expiry[key] = time.time() + ttl
            elif self.default_ttl is not None:
                self.expiry[key] = time.time() + self.default_ttl
    
    def delete(self, key: str) -> bool:
        """
        Supprimer une valeur du cache.
        
        Args:
            key: La clé de la valeur à supprimer.
            
        Returns:
            True si la valeur a été supprimée, False sinon.
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.expiry:
                    del self.expiry[key]
                return True
            return False
    
    def clear(self) -> None:
        """
        Vider le cache.
        """
        with self.lock:
            self.cache.clear()
            self.expiry.clear()
    
    def cleanup(self) -> int:
        """
        Nettoyer les entrées expirées du cache.
        
        Returns:
            Le nombre d'entrées supprimées.
        """
        with self.lock:
            now = time.time()
            expired_keys = [key for key, expiry in self.expiry.items() if expiry <= now]
            
            for key in expired_keys:
                del self.cache[key]
                del self.expiry[key]
            
            return len(expired_keys)

class FileCache(Cache):
    """
    Implémentation de cache sur fichier.
    """
    def __init__(self, cache_dir: str, default_ttl: Optional[int] = None):
        """
        Initialiser le cache sur fichier.
        
        Args:
            cache_dir: Répertoire où stocker les fichiers de cache.
            default_ttl: Durée de vie par défaut en secondes (None pour une durée illimitée).
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        
        # Créer le répertoire de cache s'il n'existe pas
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """
        Obtenir le chemin du fichier de cache pour une clé donnée.
        
        Args:
            key: La clé pour laquelle obtenir le chemin.
            
        Returns:
            Le chemin du fichier de cache.
        """
        # Utiliser un hachage de la clé pour éviter les problèmes de caractères spéciaux
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.cache")
    
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Récupérer une valeur du cache.
        
        Args:
            key: La clé de la valeur à récupérer.
            
        Returns:
            Un tuple (hit, value) où hit est un booléen indiquant si la valeur a été trouvée
            et value est la valeur récupérée (ou None si hit est False).
        """
        cache_path = self._get_cache_path(key)
        
        with self.lock:
            # Vérifier si le fichier existe
            if not os.path.exists(cache_path):
                return False, None
            
            try:
                # Lire le fichier de cache
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                
                # Vérifier si la valeur a expiré
                if 'expiry' in data and data['expiry'] <= time.time():
                    os.remove(cache_path)
                    return False, None
                
                return True, data['value']
            except (IOError, pickle.PickleError) as e:
                logging.error(f"Erreur lors de la lecture du cache: {str(e)}")
                return False, None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Définir une valeur dans le cache.
        
        Args:
            key: La clé sous laquelle stocker la valeur.
            value: La valeur à stocker.
            ttl: Durée de vie en secondes (None pour utiliser la durée par défaut).
        """
        cache_path = self._get_cache_path(key)
        
        with self.lock:
            try:
                # Préparer les données à stocker
                data = {'value': value}
                
                # Définir l'expiration si nécessaire
                if ttl is not None:
                    data['expiry'] = time.time() + ttl
                elif self.default_ttl is not None:
                    data['expiry'] = time.time() + self.default_ttl
                
                # Écrire le fichier de cache
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            except (IOError, pickle.PickleError) as e:
                logging.error(f"Erreur lors de l'écriture du cache: {str(e)}")
    
    def delete(self, key: str) -> bool:
        """
        Supprimer une valeur du cache.
        
        Args:
            key: La clé de la valeur à supprimer.
            
        Returns:
            True si la valeur a été supprimée, False sinon.
        """
        cache_path = self._get_cache_path(key)
        
        with self.lock:
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    return True
                except IOError as e:
                    logging.error(f"Erreur lors de la suppression du cache: {str(e)}")
            return False
    
    def clear(self) -> None:
        """
        Vider le cache.
        """
        with self.lock:
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        os.remove(os.path.join(self.cache_dir, filename))
            except IOError as e:
                logging.error(f"Erreur lors du vidage du cache: {str(e)}")
    
    def cleanup(self) -> int:
        """
        Nettoyer les entrées expirées du cache.
        
        Returns:
            Le nombre d'entrées supprimées.
        """
        count = 0
        now = time.time()
        
        with self.lock:
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        cache_path = os.path.join(self.cache_dir, filename)
                        
                        try:
                            with open(cache_path, 'rb') as f:
                                data = pickle.load(f)
                            
                            if 'expiry' in data and data['expiry'] <= now:
                                os.remove(cache_path)
                                count += 1
                        except (IOError, pickle.PickleError):
                            # Supprimer les fichiers corrompus
                            os.remove(cache_path)
                            count += 1
            except IOError as e:
                logging.error(f"Erreur lors du nettoyage du cache: {str(e)}")
        
        return count

class CacheManager:
    """
    Gestionnaire de cache pour l'application.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CacheManager, cls).__new__(cls)
                cls._instance._init()
            return cls._instance
    
    def _init(self):
        """
        Initialiser le gestionnaire de cache.
        """
        self.caches: Dict[str, Cache] = {}
        self.default_cache = 'memory'
        
        # Créer les caches par défaut
        self.caches['memory'] = MemoryCache(default_ttl=3600)  # 1 heure
        self.caches['file'] = FileCache('data/cache', default_ttl=86400)  # 1 jour
    
    def get_cache(self, name: Optional[str] = None) -> Cache:
        """
        Obtenir un cache par son nom.
        
        Args:
            name: Le nom du cache à obtenir (None pour le cache par défaut).
            
        Returns:
            Le cache demandé.
            
        Raises:
            ValueError: Si le cache demandé n'existe pas.
        """
        if name is None:
            name = self.default_cache
        
        if name not in self.caches:
            raise ValueError(f"Le cache '{name}' n'existe pas")
        
        return self.caches[name]
    
    def add_cache(self, name: str, cache: Cache) -> None:
        """
        Ajouter un nouveau cache.
        
        Args:
            name: Le nom du cache à ajouter.
            cache: L'instance de cache à ajouter.
            
        Raises:
            ValueError: Si un cache avec ce nom existe déjà.
        """
        if name in self.caches:
            raise ValueError(f"Un cache nommé '{name}' existe déjà")
        
        self.caches[name] = cache
    
    def set_default_cache(self, name: str) -> None:
        """
        Définir le cache par défaut.
        
        Args:
            name: Le nom du cache à définir comme défaut.
            
        Raises:
            ValueError: Si le cache demandé n'existe pas.
        """
        if name not in self.caches:
            raise ValueError(f"Le cache '{name}' n'existe pas")
        
        self.default_cache = name
    
    def cleanup_all(self) -> Dict[str, int]:
        """
        Nettoyer tous les caches.
        
        Returns:
            Un dictionnaire avec le nombre d'entrées supprimées pour chaque cache.
        """
        results = {}
        
        for name, cache in self.caches.items():
            if hasattr(cache, 'cleanup'):
                results[name] = cache.cleanup()
        
        return results

# Fonctions d'aide pour accéder au gestionnaire de cache
def get_cache(name: Optional[str] = None) -> Cache:
    """
    Obtenir un cache par son nom.
    
    Args:
        name: Le nom du cache à obtenir (None pour le cache par défaut).
        
    Returns:
        Le cache demandé.
    """
    return CacheManager().get_cache(name)

def cache_get(key: str, cache_name: Optional[str] = None) -> Tuple[bool, Any]:
    """
    Récupérer une valeur du cache.
    
    Args:
        key: La clé de la valeur à récupérer.
        cache_name: Le nom du cache à utiliser (None pour le cache par défaut).
        
    Returns:
        Un tuple (hit, value) où hit est un booléen indiquant si la valeur a été trouvée
        et value est la valeur récupérée (ou None si hit est False).
    """
    return get_cache(cache_name).get(key)

def cache_set(key: str, value: Any, ttl: Optional[int] = None, cache_name: Optional[str] = None) -> None:
    """
    Définir une valeur dans le cache.
    
    Args:
        key: La clé sous laquelle stocker la valeur.
        value: La valeur à stocker.
        ttl: Durée de vie en secondes (None pour utiliser la durée par défaut).
        cache_name: Le nom du cache à utiliser (None pour le cache par défaut).
    """
    get_cache(cache_name).set(key, value, ttl)

def cache_delete(key: str, cache_name: Optional[str] = None) -> bool:
    """
    Supprimer une valeur du cache.
    
    Args:
        key: La clé de la valeur à supprimer.
        cache_name: Le nom du cache à utiliser (None pour le cache par défaut).
        
    Returns:
        True si la valeur a été supprimée, False sinon.
    """
    return get_cache(cache_name).delete(key)

def cache_clear(cache_name: Optional[str] = None) -> None:
    """
    Vider le cache.
    
    Args:
        cache_name: Le nom du cache à vider (None pour le cache par défaut).
    """
    get_cache(cache_name).clear()

def cache_get_or_set(key: str, default_factory: Callable[[], T], ttl: Optional[int] = None, 
                    cache_name: Optional[str] = None) -> T:
    """
    Récupérer une valeur du cache ou la définir si elle n'existe pas.
    
    Args:
        key: La clé de la valeur à récupérer.
        default_factory: Fonction à appeler pour obtenir la valeur par défaut.
        ttl: Durée de vie en secondes (None pour utiliser la durée par défaut).
        cache_name: Le nom du cache à utiliser (None pour le cache par défaut).
        
    Returns:
        La valeur récupérée ou définie.
    """
    return get_cache(cache_name).get_or_set(key, default_factory, ttl)

def cached(ttl: Optional[int] = None, cache_name: Optional[str] = None, key_prefix: str = ''):
    """
    Décorateur pour mettre en cache le résultat d'une fonction.
    
    Args:
        ttl: Durée de vie en secondes (None pour utiliser la durée par défaut).
        cache_name: Le nom du cache à utiliser (None pour le cache par défaut).
        key_prefix: Préfixe à ajouter à la clé de cache.
        
    Returns:
        Le décorateur.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Créer une clé de cache basée sur la fonction et ses arguments
            key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Récupérer la valeur du cache ou l'obtenir en appelant la fonction
            return cache_get_or_set(key, lambda: func(*args, **kwargs), ttl, cache_name)
        
        return wrapper
    
    return decorator

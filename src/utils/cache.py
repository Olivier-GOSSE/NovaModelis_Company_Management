"""
Cache utility module.
This module provides utilities for caching data in memory.
"""
import time
import logging
import threading
import functools
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')

# Global cache storage
_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.RLock()


def cache(
    namespace: str,
    key_func: Optional[Callable[..., str]] = None,
    ttl: Optional[int] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for caching function results.
    
    Args:
        namespace: Namespace for the cache.
        key_func: Function to generate a cache key from the function arguments.
            If None, uses a default key function that converts args and kwargs to a string.
        ttl: Time to live in seconds. If None, the cache never expires.
    
    Returns:
        Decorated function that caches results.
    
    Example:
        @cache("my_namespace", ttl=60)
        def my_function(arg1, arg2):
            # Function to cache
            return expensive_operation(arg1, arg2)
    """
    def default_key_func(*args: Any, **kwargs: Any) -> str:
        """
        Default function to generate a cache key.
        
        Args:
            *args: Function arguments.
            **kwargs: Function keyword arguments.
        
        Returns:
            Cache key as a string.
        """
        key_parts = []
        
        # Add positional arguments
        for arg in args:
            key_parts.append(str(arg))
        
        # Add keyword arguments
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}={value}")
        
        return ":".join(key_parts)
    
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        """
        Decorator function.
        
        Args:
            func: Function to decorate.
        
        Returns:
            Decorated function.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            """
            Wrapper function.
            
            Args:
                *args: Function arguments.
                **kwargs: Function keyword arguments.
            
            Returns:
                Function result, either from cache or by calling the function.
            """
            # Generate cache key
            key_generator = key_func or default_key_func
            cache_key = key_generator(*args, **kwargs)
            
            # Initialize namespace if it doesn't exist
            with _cache_lock:
                if namespace not in _cache:
                    _cache[namespace] = {}
            
            # Check if result is in cache
            with _cache_lock:
                if cache_key in _cache[namespace]:
                    cached_result, timestamp = _cache[namespace][cache_key]
                    
                    # Check if cache has expired
                    if ttl is None or time.time() - timestamp < ttl:
                        logger.debug(f"Cache hit for {func.__name__} with key {cache_key}")
                        return cast(R, cached_result)
                    else:
                        # Cache has expired, remove it
                        del _cache[namespace][cache_key]
                        logger.debug(f"Cache expired for {func.__name__} with key {cache_key}")
            
            # Cache miss, call the function
            logger.debug(f"Cache miss for {func.__name__} with key {cache_key}")
            result = func(*args, **kwargs)
            
            # Store result in cache
            with _cache_lock:
                _cache[namespace][cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    
    return decorator


def clear_cache(namespace: Optional[str] = None, key: Optional[str] = None) -> None:
    """
    Clear cache entries.
    
    Args:
        namespace: Namespace to clear. If None, clears all namespaces.
        key: Key to clear within the namespace. If None, clears all keys in the namespace.
    """
    with _cache_lock:
        if namespace is None:
            # Clear all cache
            _cache.clear()
            logger.debug("Cleared all cache")
        elif namespace in _cache:
            if key is None:
                # Clear namespace
                _cache[namespace].clear()
                logger.debug(f"Cleared cache for namespace {namespace}")
            elif key in _cache[namespace]:
                # Clear specific key
                del _cache[namespace][key]
                logger.debug(f"Cleared cache for namespace {namespace} and key {key}")


def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary of cache statistics for each namespace.
    """
    stats: Dict[str, Dict[str, Any]] = {}
    
    with _cache_lock:
        for ns, entries in _cache.items():
            stats[ns] = {
                "count": len(entries),
                "size_bytes": sum(len(str(entry)) for entry in entries.values()),
                "keys": list(entries.keys())
            }
    
    return stats


def cache_result(
    namespace: str,
    key: str,
    result: Any,
    ttl: Optional[int] = None
) -> None:
    """
    Cache a result manually.
    
    Args:
        namespace: Namespace for the cache.
        key: Cache key.
        result: Result to cache.
        ttl: Time to live in seconds. If None, the cache never expires.
    """
    with _cache_lock:
        if namespace not in _cache:
            _cache[namespace] = {}
        
        _cache[namespace][key] = (result, time.time())
    
    logger.debug(f"Manually cached result for namespace {namespace} and key {key}")


def get_cached_result(
    namespace: str,
    key: str,
    default: Optional[Any] = None,
    ttl: Optional[int] = None
) -> Any:
    """
    Get a cached result manually.
    
    Args:
        namespace: Namespace for the cache.
        key: Cache key.
        default: Default value to return if the key is not in the cache.
        ttl: Time to live in seconds. If None, the cache never expires.
    
    Returns:
        Cached result or default value.
    """
    with _cache_lock:
        if namespace not in _cache or key not in _cache[namespace]:
            return default
        
        result, timestamp = _cache[namespace][key]
        
        # Check if cache has expired
        if ttl is not None and time.time() - timestamp >= ttl:
            # Cache has expired, remove it
            del _cache[namespace][key]
            logger.debug(f"Cache expired for namespace {namespace} and key {key}")
            return default
        
        logger.debug(f"Manual cache hit for namespace {namespace} and key {key}")
        return result

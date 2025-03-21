"""
Cache utility module.
This module provides utilities for caching data.
"""
import time
import logging
import functools
from typing import Any, Dict, Callable, Optional, Tuple, TypeVar, cast

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')

# Global cache storage
_cache: Dict[str, Tuple[Any, float, Optional[float]]] = {}

def cache(
    ttl: Optional[float] = 300.0,
    key_prefix: str = "",
    key_function: Optional[Callable[..., str]] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Cache decorator for functions.
    
    Args:
        ttl: Time to live in seconds. None means cache forever.
        key_prefix: Prefix for cache keys.
        key_function: Function to generate cache key from function arguments.
            If None, a default key function is used.
    
    Returns:
        Decorated function.
    
    Example:
        @cache(ttl=60)
        def get_user(user_id):
            # Expensive operation to get user
            return user
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            # Generate cache key
            if key_function:
                cache_key = f"{key_prefix}:{key_function(*args, **kwargs)}"
            else:
                # Default key function: combine function name, args, and kwargs
                arg_key = ":".join(str(arg) for arg in args)
                kwarg_key = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{func.__name__}:{arg_key}:{kwarg_key}"
            
            # Check if result is in cache and not expired
            current_time = time.time()
            if cache_key in _cache:
                result, timestamp, expiry = _cache[cache_key]
                if expiry is None or current_time < expiry:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cast(R, result)
                else:
                    logger.debug(f"Cache expired for {cache_key}")
                    del _cache[cache_key]
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            expiry = None if ttl is None else current_time + ttl
            _cache[cache_key] = (result, current_time, expiry)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        return wrapper
    
    return decorator

def clear_cache(key_prefix: str = "") -> None:
    """
    Clear cache entries with the given prefix.
    
    Args:
        key_prefix: Prefix for cache keys to clear.
            If empty, all cache entries are cleared.
    """
    global _cache
    if not key_prefix:
        _cache = {}
        logger.debug("Cleared all cache entries")
    else:
        keys_to_delete = [k for k in _cache if k.startswith(key_prefix)]
        for k in keys_to_delete:
            del _cache[k]
        logger.debug(f"Cleared {len(keys_to_delete)} cache entries with prefix {key_prefix}")

def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the cache.
    
    Returns:
        Dictionary with cache statistics.
    """
    current_time = time.time()
    total_entries = len(_cache)
    expired_entries = sum(
        1 for _, _, expiry in _cache.values()
        if expiry is not None and current_time >= expiry
    )
    permanent_entries = sum(1 for _, _, expiry in _cache.values() if expiry is None)
    
    return {
        "total_entries": total_entries,
        "active_entries": total_entries - expired_entries,
        "expired_entries": expired_entries,
        "permanent_entries": permanent_entries
    }

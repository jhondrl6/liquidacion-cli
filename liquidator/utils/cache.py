"""
Caching utilities for performance optimization.
Provides memoization for expensive calculations.
"""

from functools import lru_cache
from typing import Dict, Any, Optional, Tuple, Hashable
import hashlib
import json


class CacheManager:
    """Manages cached calculations with automatic invalidation."""
    
    def __init__(self):
        self._params_cache: Dict[str, Any] = {}
        self._calculation_cache: Dict[str, Any] = {}
        self._current_params_hash: Optional[str] = None
    
    def generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key for function call."""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and valid."""
        return self._calculation_cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._calculation_cache[key] = value
    
    def invalidate_when_params_change(self, params: Dict[str, Any]) -> None:
        """Invalidate cache when parameters change."""
        params_hash = self._hash_params(params)
        if self._current_params_hash != params_hash:
            self._calculation_cache.clear()
            self._current_params_hash = params_hash
    
    def _hash_params(self, params: Dict[str, Any]) -> str:
        """Generate hash of parameters for comparison."""
        params_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def cache_function_result(self, cache_key: Optional[str] = None):
        """Decorator for caching function results."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = cache_key or self.generate_key(func.__name__, *args, **kwargs)
                cached_result = self.get(key)
                if cached_result is not None:
                    return cached_result
                
                result = func(*args, **kwargs)
                self.set(key, result)
                return result
            return wrapper
        return decorator


def memoize_params_dependent(cache_manager: CacheManager):
    """Memoization decorator for functions that depend on parameters."""
    def decorator(func):
        @lru_cache(maxsize=128)
        def memoized_func(*args, **kwargs):
            return func(*args, **kwargs)
        return memoized_func
    return decorator


# Global cache instance for the entire application
global_cache = CacheManager()

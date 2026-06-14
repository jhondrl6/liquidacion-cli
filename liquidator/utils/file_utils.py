import json
import os
from typing import Any

from .cache import global_cache


def ensure_directory_exists(path):
    """Ensure directory exists, create if it doesn't."""
    os.makedirs(path, exist_ok=True)


def read_json_file(file_path, use_cache=True):
    """
    Read and parse JSON file with optional caching.

    Args:
        file_path: Path to JSON file
        use_cache: Whether to use caching (default: True)

    Returns:
        Parsed JSON data
    """
    if use_cache:
        cache_key = global_cache.generate_key('read_json_file', file_path)
        cached_result = global_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

    with open(file_path, encoding="utf-8") as f:
        result = json.load(f)

    if use_cache:
        global_cache.set(cache_key, result)
    return result


def write_json_file(data: dict[str, Any], file_path, clear_cache=True):
    """
    Write data to JSON file with proper formatting.

    Args:
        data: Data to write
        file_path: Path to JSON file
        clear_cache: Whether to clear cache for this file (default: True)
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if clear_cache:
        # Invalidate cache for this file
        cache_key = global_cache.generate_key('read_json_file', file_path)
        global_cache._calculation_cache.pop(cache_key, None)

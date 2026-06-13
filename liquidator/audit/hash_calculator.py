from hashlib import sha256
import json
from typing import Dict, Any


def calculate_hash(data: Dict[str, Any]) -> str:
    """Calculate SHA-256 hash of data structure."""
    json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return f"sha256:{sha256(json_str.encode('utf-8')).hexdigest()}"


class HashCalculator:
    """Calculator for data integrity verification."""

    def __init__(self):
        pass

    def calculate_input_hash(self, input_data: Dict[str, Any]) -> str:
        """Calculate hash for input data."""
        return calculate_hash(input_data)

    def calculate_output_hash(self, output_data: Dict[str, Any]) -> str:
        """Calculate hash for output data."""
        return calculate_hash(output_data)

    def verify_integrity(self, data: Dict[str, Any], expected_hash: str) -> bool:
        """Verify that data matches expected hash."""
        actual_hash = self._calculate_hash(data)
        return actual_hash == expected_hash

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Internal hash calculation method."""
        return calculate_hash(data)

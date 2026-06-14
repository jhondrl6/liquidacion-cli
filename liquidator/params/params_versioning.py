from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VersionInfo:
    year: int
    version: str
    hash_sha256: str
    fecha_carga: str
    metadata: dict[str, Any] | None = None


class ParamsVersioning:
    """Gestiona versionamiento y trazabilidad de parametros.

    Calcula hashes SHA256 de archivos de parametros y registra versiones
    para asegurar trazabilidad y auditabilidad.
    """

    def __init__(self) -> None:
        self._versions: dict[int, VersionInfo] = {}

    def calculate_file_hash(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def calculate_data_hash(self, data: dict[str, Any]) -> str:
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def register_version(
        self, year: int, path: Path, data: dict[str, Any] | None = None
    ) -> VersionInfo:
        file_hash = self.calculate_file_hash(path)
        version_str = data.get("version", "1.0") if data else "1.0"
        metadata = data.get("metadata", {}) if data else {}
        info = VersionInfo(
            year=year,
            version=version_str,
            hash_sha256=file_hash,
            fecha_carga=datetime.now().astimezone().isoformat(),
            metadata=metadata,
        )
        self._versions[year] = info
        return info

    def get_version(self, year: int) -> VersionInfo | None:
        return self._versions.get(year)

    def verify_integrity(self, year: int, current_path: Path) -> bool:
        info = self._versions.get(year)
        if not info:
            return False
        current_hash = self.calculate_file_hash(current_path)
        return current_hash == info.hash_sha256

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {
            year: {
                "year": info.year,
                "version": info.version,
                "hash_sha256": info.hash_sha256,
                "fecha_carga": info.fecha_carga,
                "metadata": info.metadata,
            }
            for year, info in self._versions.items()
        }

"""ParamsProvider — acceso centralizado y year-aware a params/<año>.json.

Fase 1 — Tarea 1.E. Prerequisito de ejecución real con segmentos 2025/2026.

API:
  - ParamsProvider.current()             → última versión disponible (año mayor)
  - ParamsProvider.for_year(year: int)   → año explícito
  - ParamsProvider.for_date(fecha: date) → año de la fecha
  - ParamsProvider.for_range(desde, hasta) → dict {año: ParamsProvider} cubriendo el rango
"""

from __future__ import annotations

import json
import threading
from datetime import date
from pathlib import Path
from typing import Any


class ParamsProvider:
    """Acceso centralizado y year-aware a params/<año>.json.

    Las liquidaciones pueden cruzar el 1-Ene (caso canónico: 2025-11-16 a
    2026-06-09), por lo que el proveedor puede servir uno o varios años
    según el rango.
    """

    _instance: ParamsProvider | None = None  # singleton "current"
    _lock: threading.Lock = threading.Lock()
    _data: dict[str, Any] = {}
    _params_dir: Path | None = None
    _year: int | None = None  # año de los datos cargados

    # ---- Accesores tipados ---------------------------------------------------

    @property
    def SMMLV(self) -> int:
        return int(self._data["SMMLV"])

    @property
    def AUXILIO_TRANS(self) -> int:
        return int(self._data["AUXILIO_TRANS"])

    @property
    def TASA_INT_CESANTIAS(self) -> float:
        return float(self._data["TASA_INT_CESANTIAS"])

    @property
    def DIAS_BASE(self) -> float:
        return float(self._data["DIAS_BASE"])

    @property
    def TOPE_INDEMNIZACION_SMMLV(self) -> int:
        return int(self._data["TOPE_INDEMNIZACION_SMMLV"])

    @property
    def year(self) -> int | None:
        """Año de los parámetros cargados en esta instancia."""
        return self._year

    @property
    def params_version(self) -> str:
        """Versión de los parámetros (campo 'version' del JSON)."""
        return str(self._data.get("version", "unknown"))

    # ---- Serialización -------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Devuelve todos los parámetros como diccionario."""
        return dict(self._data)

    # ---- Resolución del directorio params/ -----------------------------------

    @classmethod
    def _params_dir_default(cls) -> Path:
        """Directorio params/ relativo al repo raíz.

        Resuelve desde la ubicación de este archivo:
          liquidator/core/params_provider.py → parents[2] → repo raíz
        """
        repo = Path(__file__).resolve().parents[2]
        return repo / "params"

    @classmethod
    def set_params_dir(cls, path: Path | str) -> None:
        """Sobrescribe el directorio de params (útil para tests)."""
        cls._params_dir = Path(path)

    @classmethod
    def _params_dir_resolved(cls) -> Path:
        if cls._params_dir is not None:
            return cls._params_dir
        return cls._params_dir_default()

    # ---- Factory methods -----------------------------------------------------

    @classmethod
    def current(cls) -> ParamsProvider:
        """Compatibilidad: devuelve la última versión disponible (año mayor).

        Singleton — retorna siempre la misma instancia hasta reload().
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls._load_latest()
            return cls._instance

    @classmethod
    def for_year(cls, year: int) -> ParamsProvider:
        """Carga params/<year>.json explícitamente."""
        params_dir = cls._params_dir_resolved()
        p = params_dir / f"{year}.json"
        if not p.exists():
            available = sorted(params_dir.glob("[0-9][0-9][0-9][0-9].json"))
            available_years = [f.stem for f in available]
            raise FileNotFoundError(
                f"No existe params/{year}.json en {params_dir}. "
                f"Años disponibles: {available_years or 'ninguno'}"
            )
        data = json.loads(p.read_text(encoding="utf-8"))
        inst = cls()
        inst._data = data
        inst._year = year
        return inst

    @classmethod
    def for_date(cls, fecha: date) -> ParamsProvider:
        """Params del año de la fecha dada."""
        return cls.for_year(fecha.year)

    @classmethod
    def for_range(cls, desde: date, hasta: date) -> dict[int, ParamsProvider]:
        """Devuelve {año: ParamsProvider} cubriendo todos los años del rango."""
        result: dict[int, ParamsProvider] = {}
        for year in range(desde.year, hasta.year + 1):
            result[year] = cls.for_year(year)
        return result

    @classmethod
    def _load_latest(cls) -> ParamsProvider:
        """Carga el params/<año>.json con año mayor en params/."""
        params_dir = cls._params_dir_resolved()
        year_files = sorted(params_dir.glob("[0-9][0-9][0-9][0-9].json"))
        if not year_files:
            raise FileNotFoundError(
                f"No se encontraron params/<año>.json en {params_dir}"
            )
        latest = year_files[-1]
        year = int(latest.stem)
        data = json.loads(latest.read_text(encoding="utf-8"))
        inst = cls()
        inst._data = data
        inst._year = year
        return inst

    @classmethod
    def reload(cls) -> ParamsProvider:
        """Invalida el singleton y fuerza recarga del año más reciente."""
        with cls._lock:
            cls._instance = None
        return cls.current()

    # ---- Utilidades ----------------------------------------------------------

    def __repr__(self) -> str:
        year_str = str(self._year) if self._year else "?"
        return f"ParamsProvider(year={year_str})"

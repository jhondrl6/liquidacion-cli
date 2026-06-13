import json
import os
from pathlib import Path


class ParamsError(Exception):
    """Exception for parameter loading errors."""


class ParamsSource:
    """Simple dataclass holding the resolved paths for a parameter load."""

    def __init__(self, year: int, path: Path, schema_path: Path | None = None):
        self.year = year
        self.path = Path(path) if not isinstance(path, Path) else path
        self.schema_path = (
            Path(schema_path)
            if schema_path and not isinstance(schema_path, Path)
            else schema_path
        )


class ParamsLoader:
    """Load and optionally validate JSON parameter files."""

    def __init__(self, base_dir: str | Path | None = None, validator=None):
        if base_dir is None:
            base_dir = "params"
        self.base_dir = Path(base_dir) if not isinstance(base_dir, Path) else Path(base_dir)
        # Backward compat: test_params_loader expects str attributes
        self.params_dir = str(base_dir) if not isinstance(base_dir, Path) else str(base_dir)
        self.schema_path = os.path.join(str(base_dir), "schema.json")
        self.validator = validator

    # ------------------------------------------------------------------
    # test_loader.py (pytest) API
    # ------------------------------------------------------------------

    def resolve_paths(
        self,
        year: int,
        explicit_path: str | Path | None = None,
        schema_path: str | Path | None = None,
    ) -> ParamsSource:
        """Resolve the file paths for a given year."""
        path = Path(explicit_path) if explicit_path else self.base_dir / f"{year}.json"
        sp = Path(schema_path) if schema_path else self.base_dir / "schema.json"
        return ParamsSource(year=year, path=path, schema_path=sp)

    def load_raw(self, source: ParamsSource) -> dict:
        """Load raw JSON from a ParamsSource, raising ParamsError on failure."""
        path = source.path
        if not path.exists():
            raise ParamsError(f"No se encontró el archivo: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ParamsError(f"JSON inválido en {path}")

    # ------------------------------------------------------------------
    # test_params_loader.py (unittest) API  +  shared by test_loader
    # ------------------------------------------------------------------

    def load(self, year: int, path: str | Path | None = None, validate: bool = False) -> dict:
        """Load parameter data for a year, optionally validating."""
        if path is None:
            file_path = Path(self.params_dir) / f"{year}.json"
        else:
            file_path = Path(path) if not isinstance(path, Path) else path

        if not file_path.exists():
            raise ParamsError(
                f"No se encontró el archivo de parámetros para el año {year}"
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise ParamsError("JSON inválido en archivo de parámetros")

        if validate and self.validator:
            self.validator.validate(data)

        return data

    # ------------------------------------------------------------------
    # Backward compatibility with legacy callers (engine.py)
    # ------------------------------------------------------------------

    def load_params(self, year: int) -> dict:
        """Legacy alias for ``load(year)`` used by ``LiquidacionEngine``."""
        return self.load(year)

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Feature flag: whether jsonschema is available for real validation.
# ---------------------------------------------------------------------------
try:
    import jsonschema  # noqa: F401

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class ValidationError(Exception):
    """Raised when parameter validation fails."""


class ParamsValidator:
    """Validates parameter dictionaries against a JSON Schema."""

    def __init__(self, schema: dict | None = None, schema_path: str | Path | None = None):
        self._schema: dict | None = None
        self._validator = None
        self.last_validation_message: str = ""

        if schema is not None:
            self._schema = schema
            if HAS_JSONSCHEMA:
                self._validator = jsonschema.Draft7Validator(schema)  # type: ignore[name-defined]
                self.last_validation_message = "Schema cargado"

        self._schema_path: Path | None = (
            Path(schema_path) if schema_path else None
        )

    # ------------------------------------------------------------------
    # Core validation
    # ------------------------------------------------------------------

    def validate(self, data: dict) -> bool:
        """Validate *data* against the loaded schema.

        Returns ``True`` on success.  Raises ``ValidationError`` on failure.
        """
        if not HAS_JSONSCHEMA or self._validator is None:
            self.last_validation_message = (
                "Validacion omitida (jsonschema no instalado o schema no cargado)"
            )
            return True

        errors = list(self._validator.iter_errors(data))
        if not errors:
            self.last_validation_message = "Validacion exitosa"
            return True

        messages = []
        for err in errors:
            path = " → ".join(str(p) for p in err.absolute_path)
            if path:
                messages.append(f"{path}: {err.message}")
            else:
                messages.append(err.message)

        detail = "; ".join(messages)
        self.last_validation_message = detail
        raise ValidationError(f"Schema validation fallida: {detail}")

    # ------------------------------------------------------------------
    # Schema loading from disk
    # ------------------------------------------------------------------

    def load_schema(self, path: str | Path) -> None:
        """Load a JSON Schema from a file path."""
        path = Path(path) if not isinstance(path, Path) else path

        if not HAS_JSONSCHEMA:
            self.last_validation_message = "Schema no cargado (jsonschema no instalado)"
            return

        if not path.exists():
            raise ValidationError(f"Schema no encontrado: {path}")

        try:
            with open(path, encoding="utf-8") as f:
                schema = json.load(f)
        except json.JSONDecodeError:
            raise ValidationError(f"Schema JSON invalido en {path}") from None

        self._schema = schema
        self._validator = jsonschema.Draft7Validator(schema)  # type: ignore[name-defined]
        self.last_validation_message = f"Schema cargado desde {path.name}"

    def ensure_schema_loaded(self, path: str | Path | None) -> None:
        """Ensure a schema is loaded, loading from *path* if necessary.

        If the schema is already loaded the call is a no-op.
        """
        if self._validator is not None:
            return  # already loaded

        if path is None:
            raise ValidationError("Schema path requerido para cargar el schema")

        self.load_schema(path)

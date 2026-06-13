from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from liquidator.utils.file_utils import read_json_file


class NormasRepositoryError(RuntimeError):
    """Error genérico para problemas de carga de normas."""


class NormaNotFoundError(KeyError):
    """Se lanza cuando una norma no existe en el repositorio."""


@dataclass(frozen=True)
class Norma:
    id: str
    nombre: str
    descripcion: str
    texto_relevante: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class NormasRepository:
    """Repositorio de normas legales cargadas desde params/normas.json."""

    _DEFAULT_PATH = Path(__file__).resolve().parents[2] / "params" / "normas.json"

    def __init__(
        self,
        *,
        source_path: Optional[Path | str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._source_path = Path(source_path) if source_path else self._DEFAULT_PATH
        if data is None:
            data = self._load_data(self._source_path)
        self._normas: Dict[str, Norma] = self._build_normas(data.get("normas", []))
        self._plazos = data.get("plazos_pago", {})
        self._limites = data.get("limites_legales", {})

    def _load_data(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise NormasRepositoryError(f"No se encontró el archivo de normas: {path}")
        raw = read_json_file(path)
        if "normas" not in raw:
            raise NormasRepositoryError(
                "El archivo de normas no contiene la clave 'normas'."
            )
        return raw

    def _build_normas(self, registros: Iterable[Dict[str, Any]]) -> Dict[str, Norma]:
        normas: Dict[str, Norma] = {}
        for registro in registros:
            norma_id = registro.get("id")
            if not norma_id:
                continue
            core_fields = {
                "id": norma_id,
                "nombre": registro.get("nombre", ""),
                "descripcion": registro.get("descripcion", ""),
                "texto_relevante": registro.get("texto_relevante"),
                "url": registro.get("url"),
            }
            extras = {
                key: value for key, value in registro.items() if key not in core_fields
            }
            normas[norma_id] = Norma(**core_fields, metadata=extras)
        if not normas:
            raise NormasRepositoryError("No se pudieron construir normas válidas.")
        return normas

    def list_normas(self) -> List[Norma]:
        return list(self._normas.values())

    def get_norma(self, norma_id: str) -> Norma:
        try:
            return self._normas[norma_id]
        except KeyError as exc:
            raise NormaNotFoundError(norma_id) from exc

    def get_texto(self, norma_id: str) -> str:
        norma = self.get_norma(norma_id)
        if norma.texto_relevante is None:
            raise NormasRepositoryError(
                f"La norma '{norma_id}' no tiene texto relevante disponible."
            )
        return norma.texto_relevante

    def get_url(self, norma_id: str) -> Optional[str]:
        return self.get_norma(norma_id).url

    def search(self, keyword: str) -> List[Norma]:
        keyword_lower = keyword.lower()
        return [
            norma
            for norma in self._normas.values()
            if keyword_lower in norma.nombre.lower()
            or keyword_lower in norma.descripcion.lower()
        ]

    def get_plazo_definicion(self, concepto: str) -> Dict[str, Any]:
        try:
            return dict(self._plazos[concepto])
        except KeyError as exc:
            raise NormasRepositoryError(
                f"No se encontró el concepto de plazo '{concepto}'."
            ) from exc

    def get_limite(self, clave: str) -> Dict[str, Any]:
        try:
            return dict(self._limites[clave])
        except KeyError as exc:
            raise NormasRepositoryError(
                f"No se encontró el límite legal '{clave}'."
            ) from exc

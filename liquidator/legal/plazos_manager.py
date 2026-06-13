from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Optional

from liquidator.utils.file_utils import read_json_file


class PlazosManagerError(RuntimeError):
    pass


class PagoFueraDePlazoError(PlazosManagerError):
    pass


@dataclass(frozen=True)
class Plazo:
    concepto: str
    tipo_plazo: str
    dia: int
    mes: int
    descripcion: str
    norma_ref: Optional[str]
    aplica_a: tuple[str, ...]
    calcula_fecha_limite: bool
    sancion_mora: Optional[str] = None

    @property
    def requiere_pago_inmediato(self) -> bool:
        return self.tipo_plazo == "pago_inmediato"


class PlazosManager:
    _DEFAULT_PATH = Path(__file__).resolve().parents[2] / "params" / "plazos.json"

    def __init__(
        self,
        *,
        source_path: Optional[Path | str] = None,
        data: Optional[Dict[str, Dict[str, Dict[str, object]]]] = None,
    ) -> None:
        self._source_path = Path(source_path) if source_path else self._DEFAULT_PATH
        raw = data or self._load_raw(self._source_path)
        self._plazos: Dict[str, Plazo] = self._build_plazos(raw.get("plazos_pago", {}))

    def _load_raw(self, path: Path) -> Dict[str, Dict[str, object]]:
        if not path.exists():
            raise PlazosManagerError(f"No se encontró el archivo de plazos: {path}")
        return read_json_file(path)

    def _build_plazos(
        self, registros: Dict[str, Dict[str, object]]
    ) -> Dict[str, Plazo]:
        plazos: Dict[str, Plazo] = {}
        for concepto, info in registros.items():
            aplica_a = tuple(info.get("aplica_a", []))
            plazo = Plazo(
                concepto=concepto,
                tipo_plazo=str(info.get("tipo_plazo", "")),
                dia=int(info.get("dia", 0)),
                mes=int(info.get("mes", 0)),
                descripcion=str(info.get("descripcion", "")),
                norma_ref=info.get("norma_ref"),
                aplica_a=aplica_a,
                calcula_fecha_limite=bool(info.get("calcula_fecha_limite", False)),
                sancion_mora=info.get("sancion_mora"),
            )
            plazos[concepto] = plazo
        if not plazos:
            raise PlazosManagerError("No hay plazos configurados.")
        return plazos

    def get_plazo(self, concepto: str) -> Plazo:
        try:
            return self._plazos[concepto]
        except KeyError as exc:
            raise PlazosManagerError(
                f"Concepto de plazo desconocido: {concepto}"
            ) from exc

    def calculate_fecha_limite(self, concepto: str, fecha_referencia: date) -> date:
        plazo = self.get_plazo(concepto)
        if plazo.requiere_pago_inmediato:
            return fecha_referencia
        if plazo.dia <= 0 or plazo.mes <= 0:
            raise PlazosManagerError(
                f"El plazo '{concepto}' no tiene día/mes configurado para cálculo."
            )
        year = fecha_referencia.year
        if plazo.calcula_fecha_limite:
            year += 1
        elif plazo.mes < fecha_referencia.month or (
            plazo.mes == fecha_referencia.month and plazo.dia < fecha_referencia.day
        ):
            year += 1
        return date(year, plazo.mes, plazo.dia)

    def aplica_a_modo(self, concepto: str, modo: str) -> bool:
        plazo = self.get_plazo(concepto)
        if not plazo.aplica_a:
            return True
        return modo.upper() in {item.upper() for item in plazo.aplica_a}

    def validar_fecha_pago(
        self, concepto: str, fecha_referencia: date, fecha_pago: date
    ) -> bool:
        plazo = self.get_plazo(concepto)
        limite = self.calculate_fecha_limite(concepto, fecha_referencia)
        if plazo.requiere_pago_inmediato and fecha_pago != fecha_referencia:
            raise PagoFueraDePlazoError(
                f"El concepto '{concepto}' debe pagarse el {fecha_referencia.isoformat()}"
            )
        if fecha_pago > limite:
            raise PagoFueraDePlazoError(
                f"El concepto '{concepto}' debió pagarse a más tardar el {limite.isoformat()}"
            )
        return True

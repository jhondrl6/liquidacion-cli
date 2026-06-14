from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime


class RecargoError(RuntimeError):
    pass


@dataclass(frozen=True)
class RecargoConfig:
    recargo_dominical_prev: float
    recargo_dominical_post: float
    recargo_nocturno: float
    recargo_festivo: float
    recargo_nocturno_festivo: float
    fecha_cambio_dominical: date


class RecargosManager:
    """Gestiona los recargos legales (dominical, nocturno y festivo)."""

    def __init__(
        self,
        params: Mapping[str, object],
        *,
        dominical_prev: float = 0.75,
        dominical_post: float = 0.80,
        nocturno: float = 0.35,
        festivo: float = 0.75,
        nocturno_festivo: float = 1.10,
    ) -> None:
        try:
            fecha_cambio = self._parse_fecha(
                params["FECHA_APLICACION_RECARGO_DOMINICAL"]
            )
        except KeyError as exc:
            raise ValueError(
                "Falta FECHA_APLICACION_RECARGO_DOMINICAL en parámetros"
            ) from exc
        self._config = RecargoConfig(
            recargo_dominical_prev=float(dominical_prev),
            recargo_dominical_post=float(dominical_post),
            recargo_nocturno=float(nocturno),
            recargo_festivo=float(festivo),
            recargo_nocturno_festivo=float(nocturno_festivo),
            fecha_cambio_dominical=fecha_cambio,
        )

    def _parse_fecha(self, valor: object) -> date:
        if isinstance(valor, date):
            return valor
        if isinstance(valor, str):
            return datetime.strptime(valor, "%Y-%m-%d").date()
        raise ValueError("Fecha de recargo dominical inválida")

    @property
    def fecha_cambio_dominical(self) -> date:
        return self._config.fecha_cambio_dominical

    def get_recargo_dominical(self, fecha: date) -> float:
        if fecha >= self.fecha_cambio_dominical:
            return self._config.recargo_dominical_post
        return self._config.recargo_dominical_prev

    def get_recargo_nocturno(self) -> float:
        return self._config.recargo_nocturno

    def get_recargo_festivo(self) -> float:
        return self._config.recargo_festivo

    def get_recargo_nocturno_festivo(self) -> float:
        return self._config.recargo_nocturno_festivo

    def calcular_valor_recargo(
        self,
        *,
        base: float,
        tipo: str,
        fecha: date,
        es_nocturno: bool = False,
    ) -> float:
        if base < 0:
            raise RecargoError("El valor base no puede ser negativo.")
        tipo_normalizado = tipo.lower()
        if tipo_normalizado == "dominical":
            porcentaje = self.get_recargo_dominical(fecha)
        elif tipo_normalizado == "festivo":
            porcentaje = (
                self.get_recargo_nocturno_festivo()
                if es_nocturno
                else self.get_recargo_festivo()
            )
        elif tipo_normalizado == "nocturno":
            porcentaje = self.get_recargo_nocturno()
        else:
            raise RecargoError(f"Tipo de recargo desconocido: {tipo}")
        return base * porcentaje

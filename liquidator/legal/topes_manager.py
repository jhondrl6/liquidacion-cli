from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class TopeConfig:
    smmlv: float
    limite_auxilio: float
    tope_indemnizacion_smmlv: float


class TopesManager:
    """Gestión de topes y límites legales basados en parámetros oficiales."""

    def __init__(self, params: Mapping[str, float]) -> None:
        try:
            config = TopeConfig(
                smmlv=float(params["SMMLV"]),
                limite_auxilio=float(params["LIMITE_AUXILIO"]),
                tope_indemnizacion_smmlv=float(params["TOPE_INDEMNIZACION_SMMLV"]),
            )
        except KeyError as exc:
            raise ValueError(f"Falta el parámetro requerido: {exc.args[0]}") from exc
        self._config = config

    @property
    def smmlv(self) -> float:
        return self._config.smmlv

    @property
    def limite_auxilio_transporte(self) -> float:
        """Get limite auxilio transporte value."""
        return self._config.limite_auxilio

    @property
    def tope_indemnizacion(self) -> float:
        """Calculate tope indemnizacion based on SMMLV."""
        return self._config.tope_indemnizacion_smmlv * self.smmlv

    def aplica_auxilio_transporte(self, salario_base: float) -> bool:
        """Check if auxilio transporte applies based on salary."""
        return salario_base <= self.limite_auxilio_transporte

    def aplicar_tope_indemnizacion(self, valor_calculado: float) -> float:
        """Apply indemnization tope limit."""
        return min(valor_calculado, self.tope_indemnizacion)

    def calcular_tope_por_smmlv(self, multiplicador: float) -> float:
        """Calculate tope value as multiple of SMMLV."""
        return self.smmlv * multiplicador

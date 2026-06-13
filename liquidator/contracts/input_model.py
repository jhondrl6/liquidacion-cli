"""Schema de entrada del motor: `LiquidacionInput` (Tarea 1.C base).

Modelos Pydantic v2. Forma 2 segmentada/anidada — la que el motor
produce internamente vía `WorkflowOrchestrator` y la que el plan §3 y
la KB_LLM/04 documentan como el input "real" (con `trabajador`,
`empleador`, `contrato`, `salario` en sub-objetos).

Forma 1 (plana, estilo `examples/inputs/finca_rural.json` y
`examples/inputs/test_minimo_valid.json`) la sigue aceptando el
`InputParser` legacy hasta que Tarea 1.D (refactor `JSONGenerator` y
validador unificado) consolide el contrato. Por eso este schema
exige explícitamente los sub-objetos.

Extensiones futuras (NO en esta tarea, se aplican como tareas
separadas y retrocompatibles):
- 1.C-bis (addendum SL2630): `Salario.sbl_por_anio`,
  `Salario.historial_salarial`, `MesValor`, model_validator
  `variable → requiere historial o sbl_por_anio`.
- 1.C-ter (addendum finiquito): `Contrato.motivo_terminacion` como
  `MotivoTerminacion` (enum), `VacacionesEstado` tipado
  (reemplaza `vacaciones: dict`).
- 1.C-quater (addendum preaviso): `Contrato.preaviso_entregado`,
  `fecha_preaviso`, `dias_preaviso`, `fecha_vencimiento_termino_fijo`.

Convención: 1 fase por sesión. Esta tarea sienta la base; las
extensiones se aplican en sesiones posteriores.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# --- Sub-modelos -------------------------------------------------------------


class Trabajador(BaseModel):
    """Datos del trabajador. PII sensible: NO escribir en KB ni en logs."""

    nombre: str
    documento: str


class Empleador(BaseModel):
    """Datos del empleador. PII sensible: NO escribir en KB ni en logs."""

    nombre: str
    documento: str


class Contrato(BaseModel):
    """Vínculo contractual y su ámbito temporal.

    `motivo_terminacion` se modela como `str | None` en la base 1.C.
    Tarea 1.C-ter lo convierte en enum `MotivoTerminacion` cubriendo
    Arts. 45-49 CST. Mantener retrocompatible: default `None`.
    """

    fecha_ingreso: date
    fecha_corte: date
    tipo: Literal["INDEFINIDO", "FIJO", "OBRA_LABOR", "PRESTACION"]
    motivo_terminacion: str | None = None


class Salario(BaseModel):
    """Salario base del trabajador (SBL) y sus condiciones.

    En la base 1.C `dias_trabajados` es opcional y NO se valida que
    esté presente cuando `variable=True`. Tarea 1.C-bis agrega ese
    model_validator + los campos `sbl_por_anio` y `historial_salarial`
    para anualización salarial (SL2630-2024).
    """

    SBL: Decimal = Field(gt=0)
    auxilio_transporte: bool = False
    variable: bool = False
    # Requerido si variable=True (validación se agrega en 1.C-bis).
    dias_trabajados: int | None = None


class LiquidacionInput(BaseModel):
    """Contrato de entrada del motor de liquidación (Tarea 1.C base).

    Forma 2 (segmentada/anidada) — la que produce el
    `WorkflowOrchestrator` cruzando año calendario. Ver KB_LLM/04
    §"Forma 2 — Input segmentado".

    `vacaciones` y `auxilios` se modelan como `dict | None` en la base.
    Tarea 1.C-ter los convierte en modelos tipados (`VacacionesEstado`,
    `AuxiliosEstado` cuando exista).
    """

    trabajador: Trabajador
    empleador: Empleador
    contrato: Contrato
    salario: Salario
    modo: Literal["PERIODICA", "FINIQUITO", "VACACIONES"]
    vacaciones: dict | None = None  # tipado en 1.C-ter
    auxilios: dict | None = None  # extensibilidad

    @field_validator("contrato")
    @classmethod
    def _corte_mayor_ingreso(cls, v: Contrato) -> Contrato:
        """Garantiza que el periodo de cálculo no se invierta.

        Sin esta regla, un input con `fecha_corte < fecha_ingreso`
        produciría duraciones negativas y división por cero en los
        calculadores. La regla es dura (no overrideable en v2.0).
        """
        if v.fecha_corte < v.fecha_ingreso:
            raise ValueError("fecha_corte debe ser >= fecha_ingreso")
        return v


__all__ = [
    "Trabajador",
    "Empleador",
    "Contrato",
    "Salario",
    "LiquidacionInput",
]

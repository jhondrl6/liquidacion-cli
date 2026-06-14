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
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

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

    `motivo_terminacion` usa el enum `MotivoTerminacion` (Tarea 1.C-ter,
    addendum finiquito/vacaciones). Default `None` mantiene
    retrocompatibilidad con el caso canónico PERIODICA.

    `fecha_terminacion_real` es obligatorio en modo FINIQUITO (validado
    por `LiquidacionInput._finiquito_requiere_motivo`).
    """

    fecha_ingreso: date
    fecha_corte: date
    tipo: Literal["INDEFINIDO", "FIJO", "OBRA_LABOR", "PRESTACION"]
    motivo_terminacion: MotivoTerminacion | None = None
    fecha_terminacion_real: date | None = None

    @model_validator(mode="after")
    def _terminacion_real_requiere_motivo(self) -> "Contrato":
        """Si hay fecha de terminación real, debe venir con motivo.

        Regla de integridad: no se puede declarar que el contrato terminó
        sin especificar por qué (Art. 49 CST exige causa expresa).
        """
        if self.fecha_terminacion_real and not self.motivo_terminacion:
            raise ValueError(
                "Si hay fecha_terminacion_real, es obligatorio motivo_terminacion"
            )
        return self


class MotivoTerminacion(str, Enum):
    """Motivos de terminación del contrato laboral (Arts. 45-49 CST).

    Tarea 1.C-ter (addendum finiquito/vacaciones 2026-06-11).
    El valor del enum es el string canónico que va al JSON.

    Uso: `contrato.motivo_terminacion == MotivoTerminacion.RENUNCIA_VOLUNTARIA`.
    """

    RENUNCIA_VOLUNTARIA = "renuncia_voluntaria"           # Art. 49 num. 6
    DESPIDO_SIN_JUSTA_CAUSA = "despido_sin_justa_causa"   # Art. 64
    DESPIDO_CON_JUSTA_CAUSA = "despido_con_justa_causa"   # Art. 62
    TERMINO_FIJO_VENCIDO = "termino_fijo_vencido"         # Art. 46
    OBRA_O_LABOR_TERMINADA = "obra_o_labor_terminada"     # Art. 45
    MUTUO_ACUERDO = "mutuo_acuerdo"                       # Art. 49 num. 1
    MUERTE_TRABAJADOR = "muerte_trabajador"               # Art. 49 num. 5
    MUERTE_EMPLEADOR = "muerte_empleador"                 # Art. 49 num. 4
    SUSPENSION_DEFICITARIA = "suspension_deficitaria"     # Art. 49 num. 3
    CIERRE_EMPRESA = "cierre_empresa"                     # Art. 49 num. 3


class PeriodoDisfrute(BaseModel):
    """Rango continuo de disfrute de vacaciones (histórico opcional).

    Tarea 1.C-ter (addendum finiquito/vacaciones 2026-06-11).
    """

    desde: date
    hasta: date  # inclusive


class VacacionesEstado(BaseModel):
    """Estado de vacaciones del trabajador al cierre del periodo.

    Tarea 1.C-ter (addendum finiquito/vacaciones 2026-06-11).
    Reemplaza el `dict` libre del input por un modelo tipado.
    Tipos en Decimal para soportar fracciones de día (Art. 189 + 190 CST).

    `dias_causados_proporcionales` es opcional: si el empleador no lo
    provee, el validador de consistencia no se ejecuta y el motor lo
    calculará a partir de los días de servicio (Tarea 2.B-ter).
    """

    dias_causados_proporcionales: Decimal | None = None
    dias_disfrutados: Decimal = Decimal(0)
    dias_pendientes: Decimal = Field(ge=0)
    fechas_disfrute: list[PeriodoDisfrute] | None = None

    @model_validator(mode="after")
    def _consistencia(self) -> "VacacionesEstado":
        """Si el empleador pasó dias_causados_proporcionales, validar
        que dias_pendientes no exceda el máximo causable."""
        causados = self.dias_causados_proporcionales
        if causados is not None:
            max_pendientes = causados - self.dias_disfrutados
            if self.dias_pendientes > max_pendientes:
                raise ValueError(
                    f"dias_pendientes ({self.dias_pendientes}) excede el máximo "
                    f"causable ({max_pendientes} = {causados} - {self.dias_disfrutados})"
                )
        return self


class MesValor(BaseModel):
    """Un mes con su valor de salario (Tarea 1.C-bis, addendum SL2630-2024).

    Modela un punto de la serie mensual del salario variable. El motor
    (Tarea 2.B-bis) calcula el promedio del año calendario del segmento
    a partir de los `MesValor` cuyo `año` coincida con el año del
    segmento. Cada `MesValor` representa el salario DEVENGADO en ese
    mes (no el pactado, no el proyectado).
    """

    año: int
    mes: int = Field(ge=1, le=12)
    valor: Decimal = Field(gt=0)


class Salario(BaseModel):
    """Salario base del trabajador (SBL) y sus condiciones.

    En la base 1.C `dias_trabajados` es opcional y NO se valida que
    esté presente cuando `variable=True`. Tarea 1.C-bis agrega ese
    model_validator + los campos `sbl_por_anio` y `historial_salarial`
    para anualización salarial (SL2630-2024).

    **Extensión 1.C-bis (addendum SL2630, absorción v2.0.0):**
    `sbl_por_anio` y `historial_salarial` son **opcionales y
    retrocompatibles**. El motor (Tarea 2.B-bis) intenta en este orden:
    1. `historial_salarial` → promedio del año del segmento.
    2. `sbl_por_anio[<año>]` → SBL explícito por año.
    3. `SBL` único (compatibilidad con v1.x — caso canónico).
    """

    SBL: Decimal = Field(gt=0)
    auxilio_transporte: bool = False
    variable: bool = False
    # Requerido si variable=True (validación agregada en 1.C-bis).
    dias_trabajados: int | None = None

    # --- 1.C-bis (addendum SL2630-2024, absorción v2.0.0) ---------------
    sbl_por_anio: dict[int, Decimal] | None = None
    historial_salarial: list[MesValor] | None = None

    @model_validator(mode="after")
    def _consistencia(self) -> "Salario":
        """Garantiza que `variable=True` siempre tenga cómo anualizar.

        Sin esta regla, un input con `variable=True` que solo trae
        `SBL` único sería ambiguo (¿el SBL es de qué año?). El
        model_validator corre DESPUÉS de la creación de campos, por
        lo que la presencia de `sbl_por_anio` o `historial_salarial`
        es detectable aquí.
        """
        if (
            self.variable
            and not self.historial_salarial
            and not self.sbl_por_anio
        ):
            raise ValueError(
                "Salario variable requiere historial_salarial o sbl_por_anio"
            )
        return self


class LiquidacionInput(BaseModel):
    """Contrato de entrada del motor de liquidación (Tarea 1.C base).

    Forma 2 (segmentada/anidada) — la que produce el
    `WorkflowOrchestrator` cruzando año calendario. Ver KB_LLM/04
    §"Forma 2 — Input segmentado".

    `vacaciones` usa el modelo tipado `VacacionesEstado` (Tarea 1.C-ter,
    addendum finiquito/vacaciones). Default `None` mantiene
    retrocompatibilidad con el caso canónico PERIODICA.
    `auxilios` queda como `dict | None` para extensibilidad futura.
    """

    trabajador: Trabajador
    empleador: Empleador
    contrato: Contrato
    salario: Salario
    modo: Literal["PERIODICA", "FINIQUITO", "VACACIONES"]
    vacaciones: VacacionesEstado | None = None
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

    @model_validator(mode="after")
    def _finiquito_requiere_motivo(self) -> "LiquidacionInput":
        """Modo FINIQUITO exige motivo_terminacion explícito.

        Sin esta regla, un finiquito podría generarse sin saber si
        corresponde indemnización (Art. 64, despido sin justa causa) o
        no (Art. 49 num. 6, renuncia voluntaria). El validador es duro:
        no permite FINIQUITO sin motivo declarado.
        """
        if self.modo == "FINIQUITO" and not self.contrato.motivo_terminacion:
            raise ValueError(
                "Liquidación en modo FINIQUITO requiere contrato.motivo_terminacion"
            )
        return self


__all__ = [
    "Trabajador",
    "Empleador",
    "Contrato",
    "MotivoTerminacion",
    "PeriodoDisfrute",
    "VacacionesEstado",
    "Salario",
    "MesValor",
    "LiquidacionInput",
]

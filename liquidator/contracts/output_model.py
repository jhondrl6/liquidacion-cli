"""Schema de salida del motor: `LiquidacionResult` (Tarea 1.C base).

Modela el shape del `liquidacion_result.json` que documenta
KB_LLM/05 y el plan §3 (línea 156): meta / trabajador / parametros /
desglose / total_liquidacion / validaciones_y_alertas /
normas_aplicadas / compliance_report.

Este modelo es la **forma observable externamente**: el motor la
produce y los generadores (JSONGenerator en 1.D, markdown en 1.F,
PDF en 1.G) la consumen. La salida del caso canónico y de los
golden tests se valida contra este schema.

Diferencias con KB_LLM/05:
- `parametros_por_segmento` se modela como `dict[str, SegmentoParams]`
  en lugar de dict libre: las claves son años calendario (string
 形式的 JSON key), el valor es sub-objeto tipado.
- `normas_aplicadas` se modela como `list[str]` (IDs de
  `params/normas.json`); KB_LLM/05 sugiere objeto con detalle, pero
  el motor histórico `liquidacion_pedro_franco.json` lo emite como
  array de strings — se mantiene compatibilidad.
- `compliance_report` se modela como `dict` libre en la base. La
  estructura interna la definirá Tarea 1.D o 1.F cuando
  `ComplianceEngine` se estabilice.

Extensiones futuras (no en esta tarea):
- Fase 2: completar `desglose` con tipos estrictos por concepto.
- Fase 3 (Tarea 3.G, 3.H): campos de auditoría inmutable y bloques
  condicionales por motivo de terminación.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field

from .input_model import Empleador, Trabajador

ComplianceStatus = Literal["GO", "WARN", "NO_GO", "OVERRIDE_APPROVED"]
ModoLiquidacion = Literal["PERIODICA", "FINIQUITO", "VACACIONES"]


# --- Sub-modelos de salida ---------------------------------------------------


class SegmentoParams(BaseModel):
    """Trazabilidad per-year de los parámetros aplicados a un segmento.

    Ver KB_LLM/05 §"`parametros_por_segmento` debe verse así para el
    caso canónico". Cada segmento (un año calendario) registra su
    `params_version` por separado, su rango, días aplicados y el path
    al archivo de parámetros usado. Esto es **crítico** para
    auditoría multi-año: reportar un único `params_version` global
    pierde la trazabilidad del segmento 2025.
    """

    params_version: str
    rango: str  # formato "YYYY-MM-DD → YYYY-MM-DD"
    dias: int = Field(ge=0)
    params_ref: str  # path relativo al repo, ej. "params/2025.json"


class MetaLiquidacion(BaseModel):
    """Metadatos de la ejecución (timestamps, hashes, compliance).

    `referencias_normativas` (KB_LLM/05): lista de IDs de
    `params/normas.json` citados. Crítico listar TANTO
    `DECRETO_1469_2025` (suspendido provisionalmente) como
    `DECRETO_159_2026` (transitorio con mismo valor) — R-LEG-07.

    `output_hash` se completa en Fase 3 (auditoría inmutable).
    """

    modo: ModoLiquidacion
    fecha_generacion: datetime
    motor_version: str
    input_hash: str
    output_hash: str | None = None
    parametros_por_segmento: dict[str, SegmentoParams]
    plantilla_version: str | None = None
    compliance_status: ComplianceStatus
    referencias_normativas: list[str] = Field(default_factory=list)


class DesgloseConcepto(BaseModel):
    """Un concepto liquidado dentro de un año calendario.

    Cada año calendario es un sub-objeto de `desglose` con esta
    forma. `indemnizacion` es `null` en v2.0 — Art. 64 CST NO se
    implementa (R-LEG-01). Los demás campos se completan en Fase 2
    (Tarea 2.A — cálculo correcto).
    """

    cesantias: Decimal | None = None
    intereses_cesantias: Decimal | None = None
    prima: Decimal | None = None
    vacaciones: Decimal | None = None
    indemnizacion: Decimal | None = None  # SIEMPRE None en v2.0 (R-LEG-01)
    recargo_dominical: Decimal | None = None


class Desglose(BaseModel):
    """Desglose agrupado por año calendario (no plano).

    Ver KB_LLM/05 §"`desglose` — Conceptos liquidados, agrupados por
    año". El motor histórico lo emite como dict libre; en v2.0 se
    restringe a `dict[str, DesgloseConcepto]` con claves = años
    calendario como strings.
    """

    # La forma mínima es dict[str, DesgloseConcepto], pero en la base
    # 1.C aceptamos dict libre para no romper golden tests existentes.
    # Se endurece en Fase 2 cuando los calculadores se estabilicen.
    raiz: dict[str, DesgloseConcepto] = Field(default_factory=dict)

    def __getitem__(self, anio: str) -> DesgloseConcepto:
        return self.raiz[anio]

    def __setitem__(self, anio: str, value: DesgloseConcepto) -> None:
        self.raiz[anio] = value

    def __contains__(self, anio: str) -> bool:
        return anio in self.raiz

    def __iter__(self):
        return iter(self.raiz)


# --- Modelo top-level --------------------------------------------------------


class LiquidacionResult(BaseModel):
    """Salida completa del motor — shape de `liquidacion_result.json`.

    Mantener el orden de campos estable: el motor histórico y los
    tests golden comparan serializaciones, y Pydantic v2 ordena por
    declaración. Si se reordena, regenerar golden files.
    """

    meta: MetaLiquidacion
    trabajador: Trabajador
    empleador: Empleador
    parametros: dict[str, Any]  # eco de los `params/<año>.json` aplicados
    desglose: Desglose
    total_liquidacion: Decimal = Field(ge=0)
    validaciones_y_alertas: dict[str, Any] = Field(default_factory=dict)
    normas_aplicadas: list[str] = Field(default_factory=list)
    compliance_report: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "ComplianceStatus",
    "ModoLiquidacion",
    "SegmentoParams",
    "MetaLiquidacion",
    "DesgloseConcepto",
    "Desglose",
    "LiquidacionResult",
    # Re-exports para conveniencia al consumidor
    "Empleador",
    "Trabajador",
]

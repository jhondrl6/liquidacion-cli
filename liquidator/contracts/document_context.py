"""Document Context — Modelo Pydantic formal para el contexto de renderizado.

Tarea 3.A (Fase 3 base, plan §8.2 línea 3197).

Diferencia clave con ``LiquidacionResult`` (ver ``output_model.py``):

- ``LiquidacionResult``: output crudo del motor. Contiene PII, datos de
  cálculo, normas, y la estructura completa que el motor emite.
- ``DocumentContext`` (este módulo): snapshot INMUTABLE y ANONIMIZADO que
  consume la capa de presentación. El input viene sin PII y el desglose
  está tipado como ``list[RenglonDesglose]`` con evidencia legal por
  renglón.

Este modelo NO reemplaza a ``LiquidacionResult``; lo complementa. El
constructor ``DocumentContext.from_engine_result()`` se ocupa de:

1. Anonimizar ``trabajador.nombre`` y ``trabajador.documento`` (y
   empleador), conforme a regla AGENTS.md #6.
2. Aplanar el ``desglose`` segmentado (``{"2025": {...}, "2026": {...}}``)
   o plano (``{"cesantias": {"valor": ..., "dias_liquidados": ...}}``)
   a una ``list[RenglonDesglose]``.
3. Extraer compliance desde ``compliance_report`` tolerando ambas
   formas (``status`` o ``compliance_status``).
4. Calcular ``total`` desde ``total_liquidacion``.

Uso::

    from liquidator.contracts.document_context import DocumentContext
    ctx = DocumentContext.from_engine_result(result_dict)
    # ctx.input["trabajador"]["documento"] == "-"
    # ctx.desglose[0].evidencia_legal == "CST Art. 249"
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ComplianceStatus = Literal["GO", "WARN", "NO_GO", "OVERRIDE_APPROVED"]


# ---------------------------------------------------------------------------
# Sub-modelos
# ---------------------------------------------------------------------------


class RenglonDesglose(BaseModel):
    """Un renglón del desglose con trazabilidad legal (plan §8.2 Tarea 3.A).

    Cada renglón es un concepto liquidado (cesantías, prima, etc.) con:

    - ``valor``: pesos colombianos.
    - ``formula``: fórmula matemática aplicada (snapshot, no ejecutable).
    - ``evidencia_legal``: cita CST/Ley/Decreto que respalda el cálculo.
    - ``parametros_usados``: snapshot de los parámetros aplicados (SBL,
      dias_base, etc.). Sirve para auditoría.

    No usamos ``extra='forbid'`` aquí porque ``parametros_usados`` ya
    cubre la variabilidad por concepto (SBL, dias_base, anio, etc.).
    """

    model_config = ConfigDict(extra="ignore")

    concepto: str = Field(
        ...,
        description="Identificador del concepto (cesantias, prima, etc.)",
    )
    valor: int = Field(..., ge=0, description="Valor liquidado en pesos colombianos")
    formula: str = Field(
        ...,
        description="Fórmula aplicada en formato legible (e.g. 'SBL * 160 / 360').",
    )
    evidencia_legal: str = Field(
        ...,
        description="Cita CST/Ley/Decreto que respalda el cálculo "
        "(e.g. 'CST Art. 249' o 'Ley 50/1990 Art. 99').",
    )
    parametros_usados: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot de los parámetros aplicados: SBL, dias_base, anio, etc.",
    )


class ComplianceInfo(BaseModel):
    """Información de compliance consolidada para el contexto.

    Estructura mínima: ``{status, failures, warnings, override}``.
    El motor puede emitir variantes (``status`` vs ``compliance_status``,
    ``blocking_failures`` vs ``failures``); ``from_compliance_report``
    absorbe todas.
    """

    model_config = ConfigDict(extra="ignore")

    status: ComplianceStatus = "GO"
    failures: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[dict[str, Any]] = Field(default_factory=list)
    override: dict[str, Any] | None = None

    @classmethod
    def from_compliance_report(cls, report: dict[str, Any] | None) -> ComplianceInfo:
        """Construye desde el ``compliance_report`` del motor.

        Tolerante a variantes:
        - ``status`` o ``compliance_status`` (markdown_generator usa ambas).
        - ``blocking_failures`` o ``failures``.
        - ``warnings`` o ``advertencias`` (legacy).
        """
        if not isinstance(report, dict):
            return cls(status="GO")
        status_raw = (
            report.get("status")
            or report.get("compliance_status")
            or "GO"
        )
        status_norm = str(status_raw).upper()
        # Si no es uno de los 4 conocidos, default GO (defensivo)
        if status_norm not in ("GO", "WARN", "NO_GO", "OVERRIDE_APPROVED"):
            status_norm = "GO"
        return cls(
            status=status_norm,  # type: ignore[arg-type]
            failures=list(
                report.get("blocking_failures")
                or report.get("failures")
                or []
            ),
            warnings=list(
                report.get("warnings")
                or report.get("advertencias")
                or []
            ),
            override=report.get("override"),
        )


class DocumentContext(BaseModel):
    """Contexto formal pasado al renderizador (Markdown, PDF).

    Estructura del plan §8.2 Tarea 3.A:

    - ``metadata``: meta del motor (motor_version, params_version, etc.).
    - ``input``: snapshot del input con PII anonimizada.
    - ``desglose``: lista de ``RenglonDesglose``.
    - ``total``: total liquidado.
    - ``compliance``: ``ComplianceInfo`` consolidada.
    - ``generado_en``: timestamp de construcción del contexto.
    - ``generado_por``: operador o proceso que construyó el contexto.
    """

    model_config = ConfigDict(extra="ignore")

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Meta del motor: motor_version, fecha_generacion, "
        "params_version, plantilla_version, hashes, etc.",
    )
    input: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot del input con PII anonimizada "
        "(trabajador.nombre='[ANONIMIZADO]', documento='-').",
    )
    desglose: list[RenglonDesglose] = Field(
        default_factory=list,
        description="Renglones del desglose aplanados (de segmentado por "
        "año a lista plana).",
    )
    total: int = Field(0, ge=0, description="Total liquidado en pesos colombianos")
    compliance: ComplianceInfo = Field(
        default_factory=ComplianceInfo,
        description="Estado de compliance consolidado.",
    )
    generado_en: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de construcción del contexto (naive, hora local).",
    )
    generado_por: str = Field(
        "Jhond",
        description="Operador o proceso que construyó el contexto.",
    )

    # -----------------------------------------------------------------------
    # Constructores
    # -----------------------------------------------------------------------

    @classmethod
    def from_engine_result(
        cls,
        result: dict[str, Any],
        *,
        generado_por: str = "Jhond",
    ) -> DocumentContext:
        """Construye un ``DocumentContext`` desde el ``LiquidacionResult``.

        Args:
            result: dict con la forma de ``LiquidacionResult`` (output del
                motor: meta, trabajador, empleador, contrato, salario,
                desglose, total_liquidacion, validaciones_y_alertas,
                normas_aplicadas, compliance_report).
            generado_por: operador o proceso que ejecuta la construcción
                (default: ``"Jhond"``).

        Returns:
            ``DocumentContext`` anonimizado, con desglose aplanado a
            ``list[RenglonDesglose]``.
        """
        if not isinstance(result, dict):
            raise TypeError(
                f"from_engine_result espera dict, recibió {type(result).__name__}"
            )

        meta = result.get("meta", {}) or {}
        return cls(
            metadata=_extract_metadata(meta),
            input=_anonymize_input(result),
            desglose=_flatten_desglose_to_renglones(result.get("desglose", {})),
            total=int(result.get("total_liquidacion", 0) or 0),
            compliance=ComplianceInfo.from_compliance_report(
                result.get("compliance_report", {})
            ),
            generado_por=generado_por,
        )


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

# Tablas de fórmulas/evidencias por concepto (fallback cuando el motor no las
# emite explícitamente). Mantener sincronizadas con KB_LLM/01 antes de
# release; marcadas como fallback.
_FORMULA_POR_CONCEPTO: dict[str, str] = {
    "cesantias": "(SBL * dias_liquidados) / 360",
    "intereses_cesantias": "(cesantias * 12%)",
    "prima": "(SBL * dias_liquidados_semestre) / 360",
    "vacaciones": "(SBL * dias_pendientes) / 720",
    "indemnizacion": "NO IMPLEMENTADA en v2.0 (R-LEG-01)",
    "salario_pendiente": "SBL * dias_pendientes / 30",
    "indemnizacion_preaviso": "(SBL / 30) * dias_faltantes",
}

_EVIDENCIA_POR_CONCEPTO: dict[str, str] = {
    "cesantias": "CST Art. 249",
    "intereses_cesantias": "CST Art. 256 (Ley 50/1990 Art. 99)",
    "prima": "CST Art. 306",
    "vacaciones": "CST Art. 186",
    "indemnizacion": "CST Art. 64 (NO implementada en v2.0, R-LEG-01)",
    "salario_pendiente": "CST Art. 134",
    "indemnizacion_preaviso": "CST Art. 46 (Tarea 2.B-cuater)",
}


def _formula_for_concept(concept: str) -> str:
    return _FORMULA_POR_CONCEPTO.get(concept, "Ver KB_LLM/01")


def _evidencia_for_concept(concept: str) -> str:
    return _EVIDENCIA_POR_CONCEPTO.get(concept, "Ver KB_LLM/01")


def _extract_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """Extrae metadata consolidada del meta del motor.

    Soporta ``parametros_por_segmento`` (multi-año) consolidando a una
    sola string con versiones únicas ordenadas.
    """
    out: dict[str, Any] = {
        "motor_version": meta.get("motor_version"),
        "fecha_generacion": meta.get("fecha_generacion"),
        "modo": meta.get("modo"),
        "params_version": _extract_params_version(meta),
        "plantilla_version": meta.get("plantilla_version"),
        "input_hash": meta.get("input_hash"),
        "output_hash": meta.get("output_hash"),
        "compliance_status": meta.get("compliance_status"),
    }
    return {k: v for k, v in out.items() if v is not None}


def _extract_params_version(meta: dict[str, Any]) -> str | None:
    """Consolida ``params_version`` desde ``parametros_por_segmento``."""
    por_seg = meta.get("parametros_por_segmento")
    if isinstance(por_seg, dict) and por_seg:
        versions = sorted(
            {
                v.get("params_version", "")
                for v in por_seg.values()
                if isinstance(v, dict) and v.get("params_version")
            }
        )
        return "+".join(versions) if versions else None
    return meta.get("params_version")


def _flatten_desglose_to_renglones(desglose: Any) -> list[RenglonDesglose]:
    """Convierte el ``desglose`` del motor a ``list[RenglonDesglose]``.

    Soporta dos formas (ver ``_build_context`` en markdown_generator.py):

    - **Segmentado**: ``{"2025": {"cesantias": 1000, ...}, "2026": {...}}``
      (valores escalares, no dicts).
    - **Plano**: ``{"cesantias": {"valor": 1000, "dias_liquidados": 160, ...}, ...}``
    """
    if not isinstance(desglose, dict):
        return []
    out: list[RenglonDesglose] = []

    # Detectar forma segmentada: claves que parecen años (4 dígitos).
    year_keys = [
        k for k in desglose
        if isinstance(k, str) and k.isdigit() and len(k) == 4
    ]

    if year_keys:
        for year in sorted(year_keys):
            year_data = desglose[year] or {}
            if not isinstance(year_data, dict):
                continue
            for concept, value in year_data.items():
                if value is None or value == 0:
                    continue
                out.append(
                    RenglonDesglose(
                        concepto=str(concept),
                        valor=int(value) if isinstance(value, (int, float)) else 0,
                        formula=_formula_for_concept(str(concept)),
                        evidencia_legal=_evidencia_for_concept(str(concept)),
                        parametros_usados={"anio": year},
                    )
                )
    else:
        for concept, data in desglose.items():
            if not isinstance(data, dict):
                continue
            valor = data.get("valor", 0) or 0
            if valor == 0:
                continue
            out.append(
                RenglonDesglose(
                    concepto=str(concept),
                    valor=int(valor),
                    formula=str(
                        data.get("formula") or _formula_for_concept(str(concept))
                    ),
                    evidencia_legal=str(
                        data.get("norma") or _evidencia_for_concept(str(concept))
                    ),
                    parametros_usados=dict(data.get("parametros_usados", {}) or {}),
                )
            )

    return out


def _anonymize_input(result: dict[str, Any]) -> dict[str, Any]:
    """Anonimiza PII en el snapshot del input (regla AGENTS.md #6).

    - ``trabajador.nombre`` → ``"[ANONIMIZADO]"``
    - ``trabajador.documento`` → ``"-"``
    - ``empleador.nombre`` → ``"[ANONIMIZADO]"``
    - ``empleador.documento`` → ``"-"``

    El resto (contrato, salario, modo) se preserva porque es necesario
    para la presentación (fechas, tipo, SBL).
    """
    out: dict[str, Any] = {}

    trab = result.get("trabajador", {}) or {}
    if isinstance(trab, dict):
        out["trabajador"] = {
            **trab,
            "nombre": "[ANONIMIZADO]",
            "documento": "-",
        }

    emp = result.get("empleador", {}) or {}
    if isinstance(emp, dict):
        out["empleador"] = {
            **emp,
            "nombre": "[ANONIMIZADO]",
            "documento": "-",
        }

    cto = result.get("contrato", {}) or {}
    if isinstance(cto, dict):
        out["contrato"] = dict(cto)

    sal = result.get("salario", {}) or {}
    if isinstance(sal, dict):
        out["salario"] = dict(sal)

    # Modo (top-level o meta)
    out["modo"] = (
        result.get("modo")
        or result.get("meta", {}).get("modo")
    )

    return out


__all__ = [
    "ComplianceInfo",
    "ComplianceStatus",
    "DocumentContext",
    "RenglonDesglose",
]

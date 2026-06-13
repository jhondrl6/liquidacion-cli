"""Generador de salida JSON del motor — v2.0.

Tarea 1.D — refactor con ParamsProvider year-aware y schema opcional.

Cambios obligatorios (plan §6.2 línea 1460):
1. ``__init__(self, schema_path=None, params=None)``.
2. Si ``params`` no se pasa, leer de ``ParamsProvider.current().to_dict()``.
3. Eliminar constantes hardcodeadas (SMMLV=1423500, AUXILIO_TRANS=200000, etc.).
4. Usar ``validaciones_y_alertas`` consistentemente.
5. Validar salida contra un JSON Schema si ``schema_path`` apunta a un archivo
   existente. Si el archivo no existe, omitir la validación (no fallar).

Compatibilidad:
- ``generate_json(input_data, calc, comp, params)`` se conserva como shim
  deprecated que arma el dict unificado y delega a ``generate_output``.
- ``save_to_file`` se mantiene (alias ``save_json``) para tests previos.
- ``_calculate_hash`` se preserva (uso interno y para tests).
"""

from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional, Union

from liquidator import __version__
from liquidator.core.params_provider import ParamsProvider

PathLike = Union[str, Path]


class JSONGenerator:
    """Genera ``liquidacion_result.json`` en el shape del Pydantic
    ``LiquidacionResult`` (Tarea 1.C).

    La forma observable externamente::

        {
            "meta": {
                "modo": "PERIODICA" | "FINIQUITO" | "VACACIONES",
                "fecha_generacion": "ISO-8601",
                "motor_version": "0.2.0-dev",
                "generator_version": "0.2.0-dev",
                "params_version": "2026-06-09",
                "params_hash": "sha256:...",
                "input_hash": "sha256:...",
                "output_hash": "sha256:...",
                "parametros_por_segmento": {...},
                "compliance_status": "GO" | "WARN" | "NO_GO" | "OVERRIDE_APPROVED",
                "referencias_normativas": ["DECRETO_1469_2025", ...],
                "plantilla_version": None,
            },
            "trabajador": {...},
            "empleador": {...},
            "parametros": {...},          # eco de params/<año>.json aplicados
            "contrato": {...},
            "desglose": {...},            # por año calendario
            "total_liquidacion": Decimal,
            "validaciones_y_alertas": {...},
            "normas_aplicadas": [...],
            "compliance_report": {...},
        }
    """

    def __init__(
        self,
        schema_path: Optional[PathLike] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        # `schema_path` puede ser string, Path, o None. Si es un archivo
        # existente, se usará para validar la salida. Si no, se ignora
        # silenciosamente (no falla el generador por ausencia de schema).
        self.schema_path: Optional[Path] = None
        if schema_path is not None:
            sp = Path(schema_path)
            if sp.is_file():
                self.schema_path = sp

        # `params` se resuelve siempre a un dict. Si no se inyectan, se
        # toman del ParamsProvider singleton (año mayor disponible). Esto
        # elimina los SMMLV=1423500 hardcodeados del refactor previo.
        self.params: Dict[str, Any] = (
            dict(params) if params is not None else ParamsProvider.current().to_dict()
        )

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------
    def generate_output(self, calculation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Genera la salida canónica del motor.

        ``calculation_result`` debe ser un dict unificado con los datos
        producidos por ``WorkflowOrchestrator`` + ``ComplianceEngine``,
        convenientemente merged por el engine.

        Claves esperadas (todas opcionales salvo ``desglose``):

        - ``input_data``        → dict con ``trabajador``, ``empleador``,
          ``contrato``, ``modo``, ``fecha_ingreso``, ``fecha_corte``.
          Como fallback, ``calculation_result`` puede traer
          ``trabajador``/``empleador``/``contrato`` en top-level.
        - ``calculation_results`` → sub-dict con ``desglose`` y
          ``total_liquidacion``. Como fallback, ``desglose`` y
          ``total_liquidacion`` en top-level.
        - ``validaciones_y_alertas`` → dict[str, str] (o top-level).
        - ``normas_aplicadas``     → list[str] (o top-level).
        - ``compliance_report``    → dict (o top-level ``compliance``).
        - ``modo``                 → "PERIODICA" | "FINIQUITO" | "VACACIONES".
        - ``referencias_normativas`` → list[str] opcional.

        La forma de retorno es la del Pydantic ``LiquidacionResult``
        (Tarea 1.C, S16). Si ``self.schema_path`` apunta a un archivo
        JSON Schema, se valida la salida con ``jsonschema.validate``.
        """
        input_data = self._extract_input(calculation_result)
        calc = self._extract_calc(calculation_result)
        compliance = self._extract_compliance(calculation_result)
        validaciones = self._extract_validaciones(calculation_result)
        normas = self._extract_normas(calculation_result)
        modo = self._extract_modo(calculation_result, input_data)
        referencias = self._extract_referencias(calculation_result, compliance)

        # Calcula input_hash a partir del input (no del calculation_result
        # entero, porque este último incluye output_hash cíclico).
        input_hash = self._calculate_hash(input_data)

        # Construye meta con todos los campos del Pydantic MetaLiquidacion
        meta = {
            "modo": modo,
            "fecha_generacion": datetime.now().isoformat(),
            "motor_version": __version__,
            "generator_version": __version__,
            "params_version": str(self.params.get("version", "unknown")),
            "params_hash": self._calculate_hash(self._params_canonical()),
            "input_hash": input_hash,
            "output_hash": None,  # se completa al final
            "parametros_por_segmento": calc.get(
                "parametros_por_segmento", {}
            ),
            "compliance_status": compliance.get(
                "compliance_status", "GO"
            ),
            "referencias_normativas": referencias,
            "plantilla_version": None,
        }

        output: Dict[str, Any] = {
            "meta": meta,
            "trabajador": input_data.get("trabajador", {}),
            "empleador": input_data.get("empleador", {}),
            "parametros": dict(self.params),
            "contrato": input_data.get("contrato", {}),
            "desglose": calc.get("desglose", {}),
            "total_liquidacion": calc.get("total_liquidacion", 0),
            "validaciones_y_alertas": validaciones,
            "normas_aplicadas": normas,
            "compliance_report": compliance,
        }

        # Completar output_hash con el SHA-256 del output SIN output_hash
        meta["output_hash"] = self._calculate_hash(output)
        output["meta"] = meta

        # Validación opcional contra JSON Schema.
        if self.schema_path is not None:
            self._validate_against_schema(output)

        return output

    # ------------------------------------------------------------------
    # Shims de compatibilidad (deprecated; mantener hasta Fase 4 cleanup)
    # ------------------------------------------------------------------
    def generate_json(
        self,
        input_data: Dict[str, Any],
        calculation_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """DEPRECATED — usar :meth:`generate_output` con un dict unificado.

        Se conserva la firma de 4 argumentos para no romper el engine ni
        los tests de Fase 0. Internamente arma el dict unificado y delega.
        """
        unified: Dict[str, Any] = {}
        if input_data:
            unified["input_data"] = input_data
        if calculation_result:
            unified.update(calculation_result)
            unified["calculation_results"] = calculation_result
        if compliance_result:
            unified["compliance_report"] = compliance_result
        # Si la `params` cambió, reconstruir el provider en la propia
        # llamada. No modificamos self (es stateful del caller).
        if params is not None:
            self.params = dict(params)
        return self.generate_output(unified)

    def save_to_file(self, output: Dict[str, Any], filepath: PathLike) -> None:
        """Escribe la salida a disco en formato JSON legible."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, sort_keys=True)

    # Alias histórico (tests previos usaban ``save_json``).
    def save_json(self, output: Dict[str, Any], filepath: PathLike) -> bool:
        """Alias de :meth:`save_to_file` que retorna ``True`` siempre."""
        self.save_to_file(output, filepath)
        return True

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _calculate_hash(self, data: Any) -> str:
        """SHA-256 estable sobre la representación canónica de ``data``.

        Usa ``sort_keys=True`` y separadores compactos para que dos dicts
        con el mismo contenido (distinto orden de claves) produzcan el
        mismo hash.
        """
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
        return f"sha256:{sha256(serialized.encode('utf-8')).hexdigest()}"

    def _params_canonical(self) -> Dict[str, Any]:
        """Subconjunto canónico de ``self.params`` que se hashea.

        Excluye campos volátiles o muy largos que no aportan a la
        trazabilidad (ej. ``referencia`` larga del 2026). Mantiene los
        numéricos y el ``version``.
        """
        return {
            k: v
            for k, v in self.params.items()
            if k
            in {
                "SMMLV",
                "AUXILIO_TRANS",
                "LIMITE_AUXILIO",
                "TASA_INT_CESANTIAS",
                "DIAS_BASE",
                "VACACIONES_DENOM",
                "REDONDEO",
                "TOPE_INDEMNIZACION_SMMLV",
                "FECHA_APLICACION_RECARGO_DOMINICAL",
                "version",
            }
        }

    def _validate_against_schema(self, output: Dict[str, Any]) -> None:
        """Valida ``output`` contra el JSON Schema en ``self.schema_path``.

        Importa ``jsonschema`` lazy para no acoplar el módulo. Si el
        paquete no está instalado, se omite (warning no fatal).
        """
        schema_path = self.schema_path
        if schema_path is None:  # type narrowing para type checkers
            return
        try:
            import jsonschema  # type: ignore
        except ImportError:  # pragma: no cover - jsonschema no instalado
            return

        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.validate(instance=output, schema=schema)
        except Exception as e:  # pragma: no cover - errores de validación
            raise ValueError(
                f"Salida del JSONGenerator no conforme al schema "
                f"{schema_path}: {e}"
            ) from e

    # ---- Extractors tolerantes a múltiples shapes ---------------------

    @staticmethod
    def _extract_input(cr: Dict[str, Any]) -> Dict[str, Any]:
        if "input_data" in cr and isinstance(cr["input_data"], dict):
            return cr["input_data"]
        # Fallback: top-level
        return {
            k: cr.get(k)
            for k in ("trabajador", "empleador", "contrato")
            if cr.get(k) is not None
        }

    @staticmethod
    def _extract_calc(cr: Dict[str, Any]) -> Dict[str, Any]:
        if "calculation_results" in cr and isinstance(cr["calculation_results"], dict):
            return cr["calculation_results"]
        return {
            k: cr.get(k)
            for k in ("desglose", "total_liquidacion", "parametros_por_segmento")
            if cr.get(k) is not None
        }

    @staticmethod
    def _extract_compliance(cr: Dict[str, Any]) -> Dict[str, Any]:
        return (
            cr.get("compliance_report")
            or cr.get("compliance")
            or {}
        )

    @staticmethod
    def _extract_validaciones(cr: Dict[str, Any]) -> Dict[str, Any]:
        return cr.get("validaciones_y_alertas", {}) or {}

    @staticmethod
    def _extract_normas(cr: Dict[str, Any]) -> list:
        normas = cr.get("normas_aplicadas", []) or []
        if not isinstance(normas, list):
            return []
        return [str(n) for n in normas]

    @staticmethod
    def _extract_modo(cr: Dict[str, Any], input_data: Dict[str, Any]) -> str:
        for src in (cr, input_data):
            modo = src.get("modo")
            if modo:
                # Normalizamos a mayúsculas para matchear el Pydantic Literal
                return str(modo).upper()
        return "PERIODICA"

    @staticmethod
    def _extract_referencias(
        cr: Dict[str, Any], compliance: Dict[str, Any]
    ) -> list:
        refs = cr.get("referencias_normativas")
        if refs:
            return [str(r) for r in refs]
        comp_refs = compliance.get("referencias_normativas")
        if comp_refs:
            return [str(r) for r in comp_refs]
        return []


__all__ = ["JSONGenerator"]

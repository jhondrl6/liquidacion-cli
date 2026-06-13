"""Tests para JSONGenerator v2.0 — Tarea 1.D refactor.

Validaciones (plan §6.2 líneas 1497-1508 + extensiones):
- Constructor sin args → defaults a ``ParamsProvider.current().to_dict()``.
- Constructor con ``params=`` → usa los inyectados.
- Constructor con ``schema_path=`` → activa validación si el archivo existe.
- Constructor con ``schema_path=`` apuntando a archivo inexistente → no falla.
- ``generate_output(calculation_result)`` retorna shape compatible con
  Pydantic ``LiquidacionResult`` (Tarea 1.C).
- ``meta.params_version`` refleja el campo ``version`` del params.
- ``meta.motor_version`` y ``meta.generator_version`` = ``__version__``.
- Hash calculation es estable independientemente del orden de claves.
- ``save_to_file`` y ``save_json`` escriben JSON válido.
- Shims deprecated ``generate_json(input, calc, comp, params)`` siguen
  funcionando (compat con Fase 0).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from liquidator import __version__
from liquidator.core.params_provider import ParamsProvider
from liquidator.output.json_generator import JSONGenerator


# ---- Fixtures --------------------------------------------------------------


@pytest.fixture
def sample_params() -> Dict[str, Any]:
    """Params sintéticos para inyección en tests (aislados del repo)."""
    return {
        "SMMLV": 999_999,
        "AUXILIO_TRANS": 1234,
        "LIMITE_AUXILIO": 2_000_000,
        "TASA_INT_CESANTIAS": 0.12,
        "DIAS_BASE": 360.0,
        "VACACIONES_DENOM": 720.0,
        "REDONDEO": 0,
        "TOPE_INDEMNIZACION_SMMLV": 20,
        "FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01",
        "version": "2026-TEST-FAKE",
    }


@pytest.fixture
def sample_input_data() -> Dict[str, Any]:
    """Input sintético con la forma de ``parsed_data`` del engine."""
    return {
        "modo": "PERIODICA",
        "fecha_ingreso": "2025-11-16",
        "fecha_corte": "2026-06-09",
        "trabajador": {
            "nombre": "[ANONIMIZADO]",
            "documento": "123456789",
        },
        "empleador": {
            "nombre": "[ANONIMIZADO]",
            "documento": "900123456",
        },
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-09",
            "tipo": "INDEFINIDO",
        },
    }


@pytest.fixture
def sample_calc_results() -> Dict[str, Any]:
    """``calculation_results`` sintético (forma de ``WorkflowResult``)."""
    return {
        "desglose": {
            "2025": {
                "cesantias": 281_111,
                "intereses_cesantias": 33_733,
                "prima": 281_111,
                "vacaciones": 140_555,
                "indemnizacion": None,
                "recargo_dominical": 0,
            },
            "2026": {
                "cesantias": 977_777,
                "intereses_cesantias": 117_333,
                "prima": 977_777,
                "vacaciones": 488_888,
                "indemnizacion": None,
                "recargo_dominical": 0,
            },
        },
        "total_liquidacion": 3_298_285,
        "SBL_GENERAL": 2_200_000,
    }


@pytest.fixture
def sample_compliance() -> Dict[str, Any]:
    """Compliance report sintético compatible con engine real."""
    return {
        "compliance_status": "GO",
        "summary": {"passed": 10, "warnings": 1, "failures": 0},
        "checks": [],
        "blocking_failures": [],
        "params_version": "2026-06-09",
    }


@pytest.fixture
def sample_validaciones() -> Dict[str, str]:
    return {
        "auxilio_transporte_excluido": "Residencia en el lugar de trabajo.",
    }


@pytest.fixture
def sample_normas() -> list:
    return [
        "Art.249-250 CST",
        "Ley 50/1990 Art.99",
        "Art.306-308 CST",
    ]


@pytest.fixture
def unified_calculation_result(
    sample_input_data: Dict[str, Any],
    sample_calc_results: Dict[str, Any],
    sample_compliance: Dict[str, Any],
    sample_validaciones: Dict[str, str],
    sample_normas: list,
) -> Dict[str, Any]:
    """Dict unificado con todo lo que el engine pasa al JSONGenerator."""
    return {
        "input_data": sample_input_data,
        "calculation_results": sample_calc_results,
        "compliance_report": sample_compliance,
        "validaciones_y_alertas": sample_validaciones,
        "normas_aplicadas": sample_normas,
    }


# ---- Constructor (DoD plan §6.2 puntos 1-2) --------------------------------


def test_json_generator_sin_args_usa_paramsprovider_current():
    """Sin args, el generador toma params del singleton year-aware."""
    g = JSONGenerator()
    # SMMLV vigente 2026 = 1.750.905 (Decreto 159/2026)
    assert g.params["SMMLV"] == 1_750_905
    assert g.params["version"] == "2026-06-09"
    assert g.schema_path is None


def test_json_generator_usa_params_inyectados(sample_params):
    """Con ``params=`` se usan los inyectados, no los del repo."""
    g = JSONGenerator(params=sample_params)
    assert g.params == sample_params
    assert g.params["SMMLV"] == 999_999
    assert g.params["version"] == "2026-TEST-FAKE"


def test_json_generator_schema_path_archivo_inexistente_no_falla(tmp_path):
    """``schema_path`` apuntando a archivo inexistente NO debe explotar."""
    ghost = tmp_path / "no-existe.schema.json"
    g = JSONGenerator(schema_path=ghost)
    assert g.schema_path is None  # se normaliza a None


def test_json_generator_schema_path_archivo_existente(tmp_path):
    """``schema_path`` apuntando a archivo válido se conserva."""
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"type": "object"}')
    g = JSONGenerator(schema_path=schema_file)
    assert g.schema_path == schema_file


# ---- generate_output (DoD plan §6.2 puntos 3-4) -----------------------------


def test_generate_output_shape_es_pydantic_compatible(
    sample_params, unified_calculation_result
):
    """La salida tiene los campos del Pydantic ``LiquidacionResult``."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(unified_calculation_result)

    # Top-level (orden estable esperado por el Pydantic)
    assert "meta" in out
    assert "trabajador" in out
    assert "empleador" in out
    assert "parametros" in out
    assert "contrato" in out
    assert "desglose" in out
    assert "total_liquidacion" in out
    assert "validaciones_y_alertas" in out
    assert "normas_aplicadas" in out
    assert "compliance_report" in out


def test_generate_output_meta_tiene_todos_los_campos(
    sample_params, unified_calculation_result
):
    """``meta`` incluye los 11 campos del Pydantic ``MetaLiquidacion``."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(unified_calculation_result)
    meta = out["meta"]

    assert meta["modo"] == "PERIODICA"
    assert meta["motor_version"] == __version__
    assert meta["generator_version"] == __version__
    assert meta["params_version"] == "2026-TEST-FAKE"  # ← del fixture
    assert meta["input_hash"].startswith("sha256:")
    assert meta["output_hash"].startswith("sha256:")
    assert meta["params_hash"].startswith("sha256:")
    assert meta["compliance_status"] == "GO"
    assert isinstance(meta["fecha_generacion"], str)
    assert isinstance(meta["parametros_por_segmento"], dict)
    assert isinstance(meta["referencias_normativas"], list)


def test_generate_output_params_reflejan_inyeccion(
    sample_params, unified_calculation_result
):
    """``out["parametros"]`` debe ser el eco de ``self.params``."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(unified_calculation_result)

    assert out["parametros"]["SMMLV"] == 999_999
    assert out["parametros"]["AUXILIO_TRANS"] == 1234
    assert out["parametros"]["version"] == "2026-TEST-FAKE"


def test_generate_output_sin_params_inyectados_usa_provider(
    unified_calculation_result,
):
    """Sin ``params=``, ``params_version`` viene del ParamsProvider vigente."""
    g = JSONGenerator()
    out = g.generate_output(unified_calculation_result)

    # ParamsProvider.current() → 2026 (año mayor)
    assert out["parametros"]["SMMLV"] == 1_750_905
    assert out["parametros"]["version"] == "2026-06-09"
    assert out["meta"]["params_version"] == "2026-06-09"


def test_generate_output_modo_normalizado_a_mayusculas(sample_params):
    """``modo`` en minúsculas o mixto se normaliza a MAYÚSCULAS."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(
        {
            "input_data": {
                "modo": "periodica",  # minúscula
                "trabajador": {"nombre": "X", "documento": "1"},
                "empleador": {"nombre": "Y", "documento": "2"},
                "contrato": {
                    "fecha_ingreso": "2025-11-16",
                    "fecha_corte": "2026-06-09",
                },
            },
            "calculation_results": {
                "desglose": {},
                "total_liquidacion": 0,
            },
            "compliance_report": {"compliance_status": "GO"},
        }
    )
    assert out["meta"]["modo"] == "PERIODICA"


def test_generate_output_maneja_validaciones_faltantes(sample_params):
    """Si no hay ``validaciones_y_alertas`` ni ``normas_aplicadas``, no falla."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(
        {
            "input_data": {
                "modo": "FINIQUITO",
                "trabajador": {"nombre": "X", "documento": "1"},
                "empleador": {"nombre": "Y", "documento": "2"},
                "contrato": {},
            },
            "calculation_results": {"desglose": {}, "total_liquidacion": 0},
            "compliance_report": {"compliance_status": "GO"},
        }
    )
    assert out["validaciones_y_alertas"] == {}
    assert out["normas_aplicadas"] == []


def test_generate_output_total_liquidacion_es_el_del_calc(sample_params):
    """``total_liquidacion`` viene de ``calculation_results``."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(
        {
            "input_data": {
                "trabajador": {"nombre": "X", "documento": "1"},
                "empleador": {"nombre": "Y", "documento": "2"},
                "contrato": {},
            },
            "calculation_results": {
                "desglose": {},
                "total_liquidacion": 9_999_999,
            },
            "compliance_report": {},
        }
    )
    assert out["total_liquidacion"] == 9_999_999


# ---- Validación contra schema (DoD plan §6.2 punto 5) ----------------------


def test_json_generator_valida_contra_schema_si_existe(
    sample_params, unified_calculation_result, tmp_path
):
    """Si el schema valida, no lanza; el output se devuelve igual."""
    # Schema minimal: top-level "object" con "meta" y "desglose" requeridos.
    schema = {
        "type": "object",
        "required": ["meta", "desglose"],
        "properties": {
            "meta": {"type": "object"},
            "desglose": {"type": "object"},
        },
    }
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema))

    g = JSONGenerator(schema_path=schema_file, params=sample_params)
    out = g.generate_output(unified_calculation_result)

    # Si llegamos aquí sin excepción, la validación pasó.
    assert "meta" in out
    assert "desglose" in out


def test_json_generator_valida_contra_schema_y_falla_si_no_cumple(
    sample_params, unified_calculation_result, tmp_path
):
    """Si el schema exige campos ausentes, lanza ``ValueError``."""
    schema = {
        "type": "object",
        "required": ["campo_que_no_existe_en_el_output"],
    }
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema))

    g = JSONGenerator(schema_path=schema_file, params=sample_params)
    with pytest.raises(ValueError, match="no conforme al schema"):
        g.generate_output(unified_calculation_result)


# ---- Hash calculation (preservado del contrato previo) ---------------------


def test_calculate_hash_estable(sample_params):
    """Mismo contenido → mismo hash, distinto orden de claves → mismo hash."""
    g = JSONGenerator(params=sample_params)
    h1 = g._calculate_hash({"a": 1, "b": 2, "c": [1, 2, 3]})
    h2 = g._calculate_hash({"c": [1, 2, 3], "b": 2, "a": 1})  # otro orden
    h3 = g._calculate_hash({"a": 1, "b": 2, "c": [1, 2, 4]})  # contenido distinto
    assert h1 == h2
    assert h1 != h3
    assert h1.startswith("sha256:")


# ---- Persistencia ----------------------------------------------------------


def test_save_to_file_escribe_json_valido(
    sample_params, unified_calculation_result, tmp_path
):
    """``save_to_file`` debe escribir JSON parseable en disco."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(unified_calculation_result)

    target = tmp_path / "resultado.json"
    g.save_to_file(out, target)

    assert target.is_file()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["meta"]["params_version"] == "2026-TEST-FAKE"
    assert loaded["desglose"]["2025"]["cesantias"] == 281_111


def test_save_json_alias_retorna_true(
    sample_params, unified_calculation_result, tmp_path
):
    """``save_json`` es alias de ``save_to_file`` y retorna ``True``."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_output(unified_calculation_result)

    target = tmp_path / "out.json"
    assert g.save_json(out, target) is True
    assert target.is_file()


# ---- Shims deprecated (compat con engine y Fase 0) ------------------------


def test_generate_json_shim_delega_a_generate_output(sample_params):
    """``generate_json`` con 4 args debe seguir funcionando (compat Fase 0)."""
    g = JSONGenerator(params=sample_params)
    out = g.generate_json(
        input_data={
            "modo": "PERIODICA",
            "trabajador": {"nombre": "X", "documento": "1"},
            "empleador": {"nombre": "Y", "documento": "2"},
            "contrato": {},
        },
        calculation_result={"desglose": {}, "total_liquidacion": 0},
        compliance_result={"compliance_status": "GO"},
        params=sample_params,
    )
    # Mismas claves que generate_output (compat con engine y tests previos)
    assert "meta" in out
    assert "desglose" in out
    assert "compliance_report" in out
    assert "validaciones_y_alertas" in out
    assert "normas_aplicadas" in out
    assert out["meta"]["params_version"] == "2026-TEST-FAKE"

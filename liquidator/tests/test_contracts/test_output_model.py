"""Tests del schema de salida (Tarea 1.C base).

Cubre el shape de `LiquidacionResult` documentado en KB_LLM/05 y
plan §3. NO ejecuta el motor — solo valida que el schema acepta y
emite los campos correctos. La integración con el motor real es
Tarea 1.D (JSONGenerator) y siguientes.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from liquidator.contracts.output_model import (
    Desglose,
    DesgloseConcepto,
    LiquidacionResult,
    MetaLiquidacion,
    SegmentoParams,
)

# --- Fixtures reutilizables -------------------------------------------------


@pytest.fixture
def meta_canonica() -> MetaLiquidacion:
    """Meta del caso canónico: 2 segmentos (2025 + 2026), referencias
    normativas que incluyen TANTO D.1469/2025 (suspendido) como
    D.159/2026 (transitorio) — R-LEG-07.
    """
    return MetaLiquidacion(
        modo="PERIODICA",
        fecha_generacion=datetime(2026, 6, 9, 12, 0, 0),
        motor_version="0.2.0-dev",
        input_hash="abc123",
        output_hash=None,
        parametros_por_segmento={
            "2025": SegmentoParams(
                params_version="2025-10-31",
                rango="2025-11-16 → 2025-12-31",
                dias=46,
                params_ref="params/2025.json",
            ),
            "2026": SegmentoParams(
                params_version="2026-06-09",
                rango="2026-01-01 → 2026-06-09",
                dias=160,
                params_ref="params/2026.json",
            ),
        },
        compliance_status="GO",
        referencias_normativas=[
            "DECRETO_1572_2024",
            "DECRETO_1573_2024",
            "DECRETO_1469_2025",
            "DECRETO_159_2026",  # R-LEG-07: transitorio con mismo valor
            "DECRETO_1470_2025",
            "LEY_2466_2025",
            "LEY50_99",
            "CST_249_252",
            "CST_306_308",
            "CST_186_192",
        ],
    )


@pytest.fixture
def desglose_canonico() -> Desglose:
    """Desglose mínimo del caso canónico: 2 años calendario."""
    desglose = Desglose()
    desglose["2025"] = DesgloseConcepto(
        cesantias=Decimal("281111"),
        intereses_cesantias=Decimal("0"),
        prima=Decimal("280889"),
        vacaciones=Decimal("0"),
        indemnizacion=None,  # R-LEG-01: Art. 64 NO implementado
        recargo_dominical=Decimal("0"),
    )
    desglose["2026"] = DesgloseConcepto(
        cesantias=Decimal("977778"),
        intereses_cesantias=Decimal("0"),
        prima=Decimal("977222"),
        vacaciones=Decimal("0"),
        indemnizacion=None,
        recargo_dominical=Decimal("0"),
    )
    return desglose


# --- Tests de sub-modelos ----------------------------------------------------


def test_meta_canonica(meta_canonica: MetaLiquidacion) -> None:
    """Meta valida con todos los campos requeridos."""
    assert meta_canonica.modo == "PERIODICA"
    assert meta_canonica.motor_version == "0.2.0-dev"
    assert meta_canonica.compliance_status == "GO"
    assert "2025" in meta_canonica.parametros_por_segmento
    assert "2026" in meta_canonica.parametros_por_segmento


def test_meta_referencias_normativas_incluye_159_2026(
    meta_canonica: MetaLiquidacion,
) -> None:
    """R-LEG-07: la salida DEBE listar D.159/2026 además de D.1469/2025.

    Si la nulidad del D.1469/2025 prospera, la liquidación sigue
    siendo legalmente trazable porque cita el decreto transitorio
    que mantiene el mismo valor.
    """
    refs = meta_canonica.referencias_normativas
    assert "DECRETO_1469_2025" in refs
    assert "DECRETO_159_2026" in refs


def test_meta_compliance_status_todos_los_valores() -> None:
    """`compliance_status` acepta los 4 estados del Literal."""
    for status in ("GO", "WARN", "NO_GO", "OVERRIDE_APPROVED"):
        meta = MetaLiquidacion(
            modo="PERIODICA",
            fecha_generacion=datetime(2026, 6, 9),
            motor_version="0.2.0-dev",
            input_hash="h",
            parametros_por_segmento={},
            compliance_status=status,
        )
        assert meta.compliance_status == status


def test_meta_compliance_status_invalido_falla() -> None:
    """`compliance_status` fuera del Literal rechaza."""
    with pytest.raises(ValidationError):
        # type: ignore[arg-type] — "PENDING" es inválido a propósito
        MetaLiquidacion(
            modo="PERIODICA",
            fecha_generacion=datetime(2026, 6, 9),
            motor_version="0.2.0-dev",
            input_hash="h",
            parametros_por_segmento={},
            compliance_status="PENDING",  # no es válido
        )


def test_segmento_params_dias_negativos_falla() -> None:
    """`dias >= 0` es regla dura: no se permiten días negativos."""
    with pytest.raises(ValidationError):
        SegmentoParams(
            params_version="2025-10-31",
            rango="2025-11-16 → 2025-12-31",
            dias=-1,
            params_ref="params/2025.json",
        )


def test_desglose_iteracion_y_acceso(desglose_canonico: Desglose) -> None:
    """Desglose se comporta como dict-like: indexación, contains, iter."""
    assert "2025" in desglose_canonico
    assert "2026" in desglose_canonico
    assert "2027" not in desglose_canonico
    assert desglose_canonico["2025"].cesantias == Decimal("281111")
    anios = list(desglose_canonico)
    assert "2025" in anios
    assert "2026" in anios


def test_desglose_concepto_indemnizacion_siempre_none() -> None:
    """R-LEG-01: `indemnizacion` SIEMPRE es None en v2.0.

    Art. 64 CST NO se implementa. El campo existe en el schema
    para compatibilidad con la forma histórica, pero el motor no
    puede emitir un valor distinto de None.
    """
    c = DesgloseConcepto(cesantias=Decimal("0"))
    assert c.indemnizacion is None


# --- Tests de LiquidacionResult top-level ------------------------------------


def test_result_completo_canonico(
    meta_canonica: MetaLiquidacion,
    desglose_canonico: Desglose,
) -> None:
    """LiquidacionResult ensambla meta + desglose + eco input + total.

    Usa `model_validate` con dict (patrón real: el motor produce
    dicts, el schema los valida y coerce sub-objetos).
    """
    result = LiquidacionResult.model_validate(
        {
            "meta": meta_canonica.model_dump(),
            "trabajador": {"nombre": "X", "documento": "1"},
            "empleador": {"nombre": "Y", "documento": "2"},
            "parametros": {"SMMLV": 1423500, "version": "2025-10-31"},
            "desglose": desglose_canonico.model_dump(),
            "total_liquidacion": "2517000",
            "normas_aplicadas": ["CST_249_252", "LEY_2466_2025"],
        }
    )
    assert result.meta.compliance_status == "GO"
    assert result.trabajador.nombre == "X"
    assert result.empleador.documento == "2"
    assert result.desglose["2025"].cesantias == Decimal("281111")
    assert result.total_liquidacion == Decimal("2517000")


def test_result_total_negativo_falla(
    meta_canonica: MetaLiquidacion,
    desglose_canonico: Desglose,
) -> None:
    """`total_liquidacion >= 0` es regla dura: nunca negativo."""
    with pytest.raises(ValidationError):
        LiquidacionResult.model_validate(
            {
                "meta": meta_canonica.model_dump(),
                "trabajador": {"nombre": "X", "documento": "1"},
                "empleador": {"nombre": "Y", "documento": "2"},
                "parametros": {},
                "desglose": desglose_canonico.model_dump(),
                "total_liquidacion": "-100",
            }
        )


def test_result_serialization_roundtrip(
    meta_canonica: MetaLiquidacion,
    desglose_canonico: Desglose,
) -> None:
    """El schema se serializa a JSON y se reconstruye sin pérdida.

    Crítico para auditoría: el golden file se almacena como JSON y
    se compara con la salida del motor serializada. Si la forma
    cambia, los golden tests fallan.
    """
    result = LiquidacionResult.model_validate(
        {
            "meta": meta_canonica.model_dump(),
            "trabajador": {"nombre": "X", "documento": "1"},
            "empleador": {"nombre": "Y", "documento": "2"},
            "parametros": {"SMMLV": 1423500},
            "desglose": desglose_canonico.model_dump(),
            "total_liquidacion": "2517000",
        }
    )
    json_str = result.model_dump_json()
    reconstruido = LiquidacionResult.model_validate_json(json_str)
    assert reconstruido.meta.modo == result.meta.modo
    assert reconstruido.total_liquidacion == result.total_liquidacion
    assert reconstruido.desglose["2025"].cesantias == Decimal("281111")


# --- Re-exports: Trabajador/Empleador accesibles desde output_model ---------


def test_trabajador_y_empleador_re_exportados() -> None:
    """Re-exports para conveniencia del consumidor."""
    from liquidator.contracts.output_model import Empleador, Trabajador

    t = Trabajador(nombre="X", documento="1")
    e = Empleador(nombre="Y", documento="2")
    assert t.nombre == "X"
    assert e.documento == "2"


# --- Regresión: tipos exportados --------------------------------------------


def test_tipos_publicos_exportados() -> None:
    """`__all__` declara exactamente los símbolos públicos."""
    from liquidator.contracts import output_model

    expected = {
        "ComplianceStatus",
        "ModoLiquidacion",
        "SegmentoParams",
        "MetaLiquidacion",
        "DesgloseConcepto",
        "Desglose",
        "LiquidacionResult",
        "Empleador",
        "Trabajador",
    }
    assert set(output_model.__all__) == expected

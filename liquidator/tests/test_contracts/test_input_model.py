"""Tests del schema de entrada (Tarea 1.C base).

Cubre el caso canónico (206d, dos segmentos, SBL=2.200.000) y los
casos de error que el modelo debe rechazar. La forma de input es la
anidada/segmentada (Forma 2 según KB_LLM/04). La Forma 1 (plana)
sigue entrando vía `InputParser` legacy — fuera de scope 1.C.

Estos tests NO cubren las extensiones 1.C-bis (Salario.sbl_por_anio),
1.C-ter (motivo_terminacion enum, VacacionesEstado) ni 1.C-quater
(preaviso) — esas tienen sus propios archivos de test.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from liquidator.contracts.input_model import (
    Empleador,
    LiquidacionInput,
    Salario,
    Trabajador,
)

# --- Fixtures reutilizables -------------------------------------------------


@pytest.fixture
def canonico_dict() -> dict:
    """Caso canónico 2025-11-16 → 2026-06-09, SBL=2.200.000, INDEFINIDO.

    Réplica del JSON anidado de KB_LLM/04 §"Forma 2" (sin `segmentos`
    porque eso lo produce el WorkflowOrchestrator, no el input del
    usuario directo).
    """
    return {
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador": {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-09",
            "tipo": "INDEFINIDO",
        },
        "salario": {"SBL": "2200000", "auxilio_transporte": False, "variable": False},
        "modo": "PERIODICA",
    }


# --- Tests positivos (caso canónico y variantes) ----------------------------


def test_input_canonico_pasa(canonico_dict: dict) -> None:
    """El input del caso ancla parsea sin errores.

    Réplica de `test_input_canonico_pasa` del plan §6.2.
    """
    inp = LiquidacionInput.model_validate(canonico_dict)
    assert inp.contrato.fecha_corte > inp.contrato.fecha_ingreso
    assert inp.contrato.tipo == "INDEFINIDO"
    assert inp.salario.SBL == Decimal("2200000")
    assert inp.modo == "PERIODICA"
    assert inp.vacaciones is None
    assert inp.auxilios is None


def test_input_canonico_coercion_int_a_decimal(canonico_dict: dict) -> None:
    """SBL como `int` debe coercionar a `Decimal` sin pérdida.

    El motor histórico acepta tanto `2200000` (int) como `"2200000"`
    (str). Pydantic v2 por defecto convierte int → Decimal. Test
    explícito para garantizar que no rompemos el comportamiento.
    """
    canonico_dict["salario"]["SBL"] = 2200000
    inp = LiquidacionInput.model_validate(canonico_dict)
    assert inp.salario.SBL == Decimal("2200000")
    assert isinstance(inp.salario.SBL, Decimal)


def test_input_canonico_sin_motivo_terminacion(canonico_dict: dict) -> None:
    """`motivo_terminacion` es opcional. PERIODICA sin motivo es válido.

    Requisito de retrocompatibilidad explícito del plan §6.1 DoD: el
    caso canónico PERIODICA sin `motivo_terminacion` debe seguir
    verde. La obligatoriedad se introduce en 1.C-ter.
    """
    inp = LiquidacionInput.model_validate(canonico_dict)
    assert inp.contrato.motivo_terminacion is None


def test_input_modo_finiquito_con_motivo(canonico_dict: dict) -> None:
    """PERIODICA + VACACIONES + FINIQUITO son los 3 modos válidos.

    En la base 1.C, FINIQUITO no exige `motivo_terminacion` (esa
    validación se agrega en 1.C-ter con `_finiquito_requiere_motivo`).
    Aquí solo validamos que el modo se acepta y el campo libre
    `motivo_terminacion` puede tomar cualquier string.
    """
    canonico_dict["modo"] = "FINIQUITO"
    canonico_dict["contrato"]["motivo_terminacion"] = "renuncia_voluntaria"
    inp = LiquidacionInput.model_validate(canonico_dict)
    assert inp.modo == "FINIQUITO"
    assert inp.contrato.motivo_terminacion == "renuncia_voluntaria"


def test_input_tipo_contrato_todos_los_valores(canonico_dict: dict) -> None:
    """`tipo` acepta los 4 valores del Literal."""
    for tipo in ("INDEFINIDO", "FIJO", "OBRA_LABOR", "PRESTACION"):
        canonico_dict["contrato"]["tipo"] = tipo
        inp = LiquidacionInput.model_validate(canonico_dict)
        assert inp.contrato.tipo == tipo


def test_input_con_vacaciones_y_auxilios(canonico_dict: dict) -> None:
    """`vacaciones` ahora es `VacacionesEstado` tipado (Tarea 1.C-ter).

    El dict debe contener al menos `dias_pendientes` (campo obligatorio
    en VacacionesEstado). `auxilios` sigue como `dict | None`.
    """
    canonico_dict["vacaciones"] = {
        "dias_causados_proporcionales": 15,
        "dias_disfrutados": 5,
        "dias_pendientes": 10,
        "fechas_disfrute": [
            {"desde": "2025-06-01", "hasta": "2025-06-15"},
        ],
    }
    canonico_dict["auxilios"] = {"conectividad": 150000}
    inp = LiquidacionInput.model_validate(canonico_dict)
    assert inp.vacaciones.dias_pendientes == Decimal("10")
    assert inp.vacaciones.dias_causados_proporcionales == Decimal("15")
    assert inp.vacaciones.dias_disfrutados == Decimal("5")
    assert len(inp.vacaciones.fechas_disfrute) == 1
    assert inp.auxilios == {"conectividad": 150000}


def test_submodelos_trabajador_y_empleador() -> None:
    """Sub-modelos son instanciables de forma independiente."""
    t = Trabajador(nombre="Juan", documento="123")
    e = Empleador(nombre="Acme", documento="900")
    assert t.nombre == "Juan"
    assert t.documento == "123"
    assert e.documento == "900"


def test_submodelo_salario_por_defecto() -> None:
    """Salario con solo SBL: defaults razonables."""
    s = Salario(SBL=Decimal("1500000"))
    assert s.auxilio_transporte is False
    assert s.variable is False
    assert s.dias_trabajados is None


# --- Tests negativos (validaciones que deben fallar) -------------------------


def test_input_corte_anterior_falla() -> None:
    """`fecha_corte < fecha_ingreso` debe lanzar `ValidationError`.

    Réplica de `test_input_corte_anterior_falla` del plan §6.2.
    Sin esta regla el motor produciría duraciones negativas.
    """
    with pytest.raises(ValidationError) as exc:
        LiquidacionInput.model_validate(
            {
                "trabajador": {"nombre": "X", "documento": "1"},
                "empleador": {"nombre": "Y", "documento": "2"},
                "contrato": {
                    "fecha_ingreso": "2026-06-15",
                    "fecha_corte": "2025-11-16",
                    "tipo": "INDEFINIDO",
                },
                "salario": {"SBL": 2200000},
                "modo": "PERIODICA",
            }
        )
    assert "fecha_corte debe ser >= fecha_ingreso" in str(exc.value)


def test_input_corte_igual_a_ingreso_pasa(canonico_dict: dict) -> None:
    """`fecha_corte == fecha_ingreso` es válido (periodo de 1 día).

    El validador usa `<` (estricto), no `<=`. Un contrato recién
    iniciado y cortado el mismo día debe poder parsear.
    """
    canonico_dict["contrato"]["fecha_ingreso"] = "2026-01-15"
    canonico_dict["contrato"]["fecha_corte"] = "2026-01-15"
    inp = LiquidacionInput.model_validate(canonico_dict)
    assert inp.contrato.fecha_corte == inp.contrato.fecha_ingreso


def test_salario_sbl_cero_falla() -> None:
    """`SBL=0` viola la restricción `Field(gt=0)`."""
    with pytest.raises(ValidationError):
        Salario(SBL=Decimal("0"))


def test_salario_sbl_negativo_falla() -> None:
    """`SBL<0` viola `Field(gt=0)`. El motor no puede calcular con
    un salario negativo — regla dura sin override."""
    with pytest.raises(ValidationError):
        Salario(SBL=Decimal("-100"))


def test_tipo_contrato_invalido_falla(canonico_dict: dict) -> None:
    """`tipo` fuera del Literal rechaza el input."""
    canonico_dict["contrato"]["tipo"] = "INDEPENDIENTE"  # no es válido
    with pytest.raises(ValidationError):
        LiquidacionInput.model_validate(canonico_dict)


def test_modo_invalido_falla(canonico_dict: dict) -> None:
    """`modo` fuera de PERIODICA|FINIQUITO|VACACIONES rechaza el input."""
    canonico_dict["modo"] = "MENSUAL"  # no es válido
    with pytest.raises(ValidationError):
        LiquidacionInput.model_validate(canonico_dict)


def test_modo_minusculas_falla(canonico_dict: dict) -> None:
    """`modo` en minúsculas no es válido (el contrato exige MAYÚSCULAS)."""
    canonico_dict["modo"] = "periodica"
    with pytest.raises(ValidationError):
        LiquidacionInput.model_validate(canonico_dict)


def test_campos_obligatorios_faltantes(canonico_dict: dict) -> None:
    """Cualquier sub-objeto obligatorio faltante rechaza el input."""
    # Falta salario
    del canonico_dict["salario"]
    with pytest.raises(ValidationError):
        LiquidacionInput.model_validate(canonico_dict)


# --- Regresión: caso ancla KB_LLM/09 ----------------------------------------


def test_caso_ancla_kb_09_estructura() -> None:
    """Réplica mínima del caso canónico documentado en KB_LLM/09.

    No ejecuta el motor — solo valida que el input parsea con la
    forma anidada que el WorkflowOrchestrator produce. La ejecución
    real del caso canónico (con cálculo de cesantías) es Tarea 1.I.
    """
    inp = LiquidacionInput.model_validate(
        {
            "trabajador": {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
            "empleador": {"nombre": "[ANONIMIZADO]", "documento": "[ANONIMIZADO]"},
            "contrato": {
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-09",
                "tipo": "INDEFINIDO",
                "fecha_terminacion_real": None,
            },
            "salario": {"SBL": 2200000, "auxilio_transporte": False, "variable": False},
            "modo": "PERIODICA",
        }
    )
    assert inp.contrato.fecha_ingreso == date(2025, 11, 16)
    assert inp.contrato.fecha_corte == date(2026, 6, 9)
    # 206 días calendario (inclusivos)
    assert (inp.contrato.fecha_corte - inp.contrato.fecha_ingreso).days == 205

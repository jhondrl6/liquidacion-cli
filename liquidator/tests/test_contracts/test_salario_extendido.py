"""Tests para Tarea 1.C-bis — Extensión de `Salario` con anualización (SL2630-2024).

Plan §6.2 Tarea 1.C-bis (líneas 893-1019) + Addendum
`addendum_sl2630_y_ipc_2026-06-09.md` §C Tarea 1.C-bis.

Esta tarea agrega a `Salario` los campos opcionales `sbl_por_anio` y
`historial_salarial` (con su sub-modelo `MesValor`) y un `model_validator`
que rechaza `variable=True` sin uno de los nuevos campos.

Decisiones de implementación (DoD):
- Aditiva retrocompatible: `Salario(SBL=...)` sin campos nuevos sigue
  funcionando idéntico al de v1.x/1.C base.
- Validación laxa en Fase 1: `sbl_por_anio` acepta cualquier `int`; la
  coerción "año debe tener `params/<año>.json`" se delega a Fase 2 vía
  `ParamsProvider.for_year(año)`.
- Cobertura: regresión simple, validación `variable=True` sin campos
  nuevos, `variable=True` con historial, `sbl_por_anio`, `MesValor` con
  mes/valor inválidos, y shape de `MesValor` válido.
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError

from liquidator.contracts.input_model import Salario, MesValor


# --- Regresión (DoD plan §6.2: input v1.x sigue funcionando idéntico) --------


def test_salario_sin_campos_nuevos_es_compatible():
    """Regresión: `Salario(SBL=...)` sin campos nuevos = comportamiento actual.

    Caso canónico (SBL 2.200.000, variable=False) debe validar idéntico al
    modelo de Tarea 1.C base. Esto garantiza que 1.C-bis NO rompe el caso
    canónico end-to-end de Fase 1 / Tarea 1.I.
    """
    s = Salario(SBL=Decimal("2200000"))
    assert s.SBL == Decimal("2200000")
    assert s.auxilio_transporte is False
    assert s.variable is False
    assert s.dias_trabajados is None
    # Campos nuevos presentes pero None (no inventados)
    assert s.sbl_por_anio is None
    assert s.historial_salarial is None


def test_salario_solo_sbl_variable_false_pasa():
    """Atajo del caso canónico: solo SBL con variable=False es válido.

    El model_validator NO debe dispararse si variable=False, aunque no
    haya historial. Esta es la garantía de retrocompatibilidad con el
    caso canónico del plan §3 (modo PERIODICA, INDEFINIDO, 206 días).
    """
    s = Salario(SBL=Decimal("1423500"), variable=False)
    assert s.variable is False


# --- Validación de consistencia (model_validator) --------------------------


def test_salario_variable_sin_historial_falla():
    """`variable=True` exige al menos uno de los nuevos campos.

    Sin esta regla, un input con `variable=True` y solo `SBL` único
    sería ambiguo (¿el SBL es de qué año calendario?). El
    model_validator rechaza con mensaje claro.
    """
    with pytest.raises(ValidationError, match="variable requiere"):
        Salario(SBL=Decimal("2200000"), variable=True)


def test_salario_variable_sin_historial_pero_con_sbl_por_anio_pasa():
    """`variable=True` con `sbl_por_anio` (sin historial) es válido.

    La prioridad 2 del motor (Tarea 2.B-bis) usa `sbl_por_anio` cuando
    no hay historial mensual. El schema debe permitir esta forma.
    """
    s = Salario(
        SBL=Decimal("2200000"),
        variable=True,
        sbl_por_anio={2025: Decimal("2200000"), 2026: Decimal("2400000")},
    )
    assert s.sbl_por_anio[2026] == Decimal("2400000")
    assert s.historial_salarial is None


def test_salario_variable_con_historial_pasa():
    """`variable=True` con `historial_salarial` es válido (recomendado).

    La prioridad 1 del motor (Tarea 2.B-bis) usa el historial mensual
    para calcular el promedio del año del segmento. Este es el caso
    del addendum §B.1.b "Completo — recomendado".
    """
    s = Salario(
        SBL=Decimal("2200000"),
        variable=True,
        historial_salarial=[
            MesValor(año=2025, mes=11, valor=Decimal("2200000")),
            MesValor(año=2025, mes=12, valor=Decimal("2200000")),
            MesValor(año=2026, mes=1, valor=Decimal("2400000")),
        ],
    )
    assert len(s.historial_salarial) == 3
    assert s.historial_salarial[0].año == 2025
    assert s.historial_salarial[0].mes == 11
    assert s.historial_salarial[0].valor == Decimal("2200000")


# --- sbl_por_anio (Forma B.1.a del addendum) -------------------------------


def test_salario_con_sbl_por_anio_pasa():
    """`sbl_por_anio` solo (sin variable=True) es válido.

    Esta forma es la B.1.a del addendum §B.1 ("Simple") — el usuario
    conoce el SBL exacto de cada año calendario. El motor en Fase 2
    lo usará cuando no haya historial mensual.
    """
    s = Salario(
        SBL=Decimal("2200000"),
        sbl_por_anio={2025: Decimal("2200000"), 2026: Decimal("2400000")},
    )
    assert s.sbl_por_anio[2026] == Decimal("2400000")
    # variable sigue siendo False (no se fuerza a True)
    assert s.variable is False


# --- MesValor: validación de rangos ----------------------------------------


def test_mesvalor_valida_rango_mes():
    """`mes` debe estar en [1, 12] (no 0, no 13)."""
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=13, valor=Decimal("2200000"))
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=0, valor=Decimal("2200000"))


def test_mesvalor_valida_valor_positivo():
    """`valor` debe ser > 0 (rechaza 0 y negativos)."""
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=6, valor=Decimal("0"))
    with pytest.raises(ValidationError):
        MesValor(año=2025, mes=6, valor=Decimal("-1000"))


def test_mesvalor_rango_mes_bordes_pasa():
    """Los bordes 1 y 12 son válidos."""
    m1 = MesValor(año=2025, mes=1, valor=Decimal("100"))
    m12 = MesValor(año=2025, mes=12, valor=Decimal("100"))
    assert m1.mes == 1
    assert m12.mes == 12


# --- Integración con LiquidacionInput (sanity check) -----------------------


def test_liquidacion_input_acepta_salario_extendido():
    """`LiquidacionInput` con `Salario` extendido valida idéntico.

    El sub-schema de `LiquidacionInput.salario` debe aceptar las nuevas
    formas sin cambio de contrato. Esto cubre la ruta completa de
    parseo del caso canónico.
    """
    from liquidator.contracts.input_model import LiquidacionInput

    inp = LiquidacionInput.model_validate({
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador": {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-15",
            "tipo": "INDEFINIDO",
        },
        "salario": {
            "SBL": 2200000,
            "variable": True,
            "historial_salarial": [
                {"año": 2025, "mes": 12, "valor": 2200000},
                {"año": 2026, "mes": 1, "valor": 2400000},
            ],
        },
        "modo": "PERIODICA",
    })
    assert inp.salario.variable is True
    assert len(inp.salario.historial_salarial) == 2
    assert inp.salario.historial_salarial[1].valor == Decimal("2400000")

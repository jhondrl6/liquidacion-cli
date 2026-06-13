"""Tests para ParamsProvider year-aware — Fase 1 / Tarea 1.E.

Validaciones del plan §6.2 (líneas 1619-1647):
  - test_params_provider_current_carga_mas_reciente
  - test_params_provider_for_year_explicito
  - test_params_provider_for_date
  - test_params_provider_for_range_cruza_anio_nuevo

Prerequisito: params/2025.json y params/2026.json existen en el repo.
"""

from datetime import date

from liquidator.core.params_provider import ParamsProvider


# ---- current() ---------------------------------------------------------------

def test_params_provider_current_carga_mas_reciente():
    """ParamsProvider.current() debe cargar el año mayor disponible (2026)."""
    p = ParamsProvider.reload()
    assert p.SMMLV > 0
    # 2026 es el año mayor con SMMLV 1.750.905
    assert p.SMMLV == 1750905
    assert p.year == 2026


# ---- for_year() --------------------------------------------------------------

def test_params_provider_for_year_explicito():
    """for_year() debe cargar el año solicitado explícitamente."""
    p2025 = ParamsProvider.for_year(2025)
    p2026 = ParamsProvider.for_year(2026)

    assert p2025.SMMLV == 1423500
    assert p2026.SMMLV == 1750905
    assert p2025.AUXILIO_TRANS == 200000
    assert p2026.AUXILIO_TRANS == 249095

    assert p2025.year == 2025
    assert p2026.year == 2026

    assert p2025.TASA_INT_CESANTIAS == 0.12
    assert p2026.TASA_INT_CESANTIAS == 0.12


def test_params_provider_for_year_inexistente():
    """for_year() con un año sin archivo debe lanzar FileNotFoundError."""
    try:
        ParamsProvider.for_year(1900)
        assert False, "Debió lanzar FileNotFoundError"
    except FileNotFoundError:
        pass


# ---- for_date() --------------------------------------------------------------

def test_params_provider_for_date():
    """for_date() selecciona el año según la fecha."""
    p = ParamsProvider.for_date(date(2025, 12, 15))
    assert p.SMMLV == 1423500
    assert p.year == 2025

    p = ParamsProvider.for_date(date(2026, 3, 15))
    assert p.SMMLV == 1750905
    assert p.year == 2026

    # Borde: 1 de enero
    p = ParamsProvider.for_date(date(2026, 1, 1))
    assert p.year == 2026
    assert p.SMMLV == 1750905


# ---- for_range() -------------------------------------------------------------

def test_params_provider_for_range_cruza_anio_nuevo():
    """for_range() debe cubrir todos los años entre desde y hasta."""
    provs = ParamsProvider.for_range(date(2025, 11, 16), date(2026, 6, 9))
    assert set(provs.keys()) == {2025, 2026}
    assert provs[2025].SMMLV == 1423500
    assert provs[2026].SMMLV == 1750905


def test_params_provider_for_range_mismo_anio():
    """for_range() con un rango dentro del mismo año devuelve un solo provider."""
    provs = ParamsProvider.for_range(date(2025, 1, 1), date(2025, 12, 31))
    assert set(provs.keys()) == {2025}
    assert provs[2025].SMMLV == 1423500


# ---- to_dict() ---------------------------------------------------------------

def test_params_provider_to_dict():
    """to_dict() devuelve todos los parámetros como diccionario."""
    p = ParamsProvider.for_year(2025)
    d = p.to_dict()
    assert isinstance(d, dict)
    assert d["SMMLV"] == 1423500
    assert d["AUXILIO_TRANS"] == 200000


# ---- params_version ----------------------------------------------------------

def test_params_provider_version():
    """params_version expone el campo 'version' del JSON."""
    p2025 = ParamsProvider.for_year(2025)
    p2026 = ParamsProvider.for_year(2026)
    assert p2025.params_version == "2025-10-31"
    assert p2026.params_version == "2026-06-09"


# ---- singleton current() -----------------------------------------------------

def test_params_provider_current_es_singleton():
    """current() retorna la misma instancia hasta reload()."""
    p1 = ParamsProvider.current()
    p2 = ParamsProvider.current()
    assert p1 is p2

    p3 = ParamsProvider.reload()
    # reload fuerza recarga; podría ser la misma data pero instancia distinta
    assert p3.SMMLV == p1.SMMLV

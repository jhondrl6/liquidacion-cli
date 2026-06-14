"""Tests unitarios de ``SalarioResolver`` — Tarea 2.B-bis.

Addendum SL2630-2024: validación de las 3 prioridades de resolución
de SBL por año calendario.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from liquidator.contracts.input_model import MesValor, Salario
from liquidator.core.salario_resolver import (
    SalarioResolver,
    SegmentoCalculo,
    segmentar_periodo,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seg(anio: int, dias: int) -> SegmentoCalculo:
    """Fabrica un ``SegmentoCalculo`` mínimo para tests."""
    return SegmentoCalculo(
        anio=anio,
        desde=date(anio, 1, 1),
        hasta=date(anio, 12, 31),
        sbl=Decimal("0"),
        dias=dias,
    )


# ---------------------------------------------------------------------------
# Prioridad 3 — SBL único (compatibilidad v1.x)
# ---------------------------------------------------------------------------


class TestPrioridad3SBLUnico:
    """El caso canónico sin campos nuevos cae al SBL único."""

    def test_prioridad_3_sbl_unico_compatibilidad(self):
        s = Salario(SBL=Decimal("2200000"))
        r = SalarioResolver(s)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")
        assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2200000")

    def test_prioridad_3_con_campos_nuevos_vacios(self):
        """sbl_por_anio=None, historial_salarial=None → cae a SBL único."""
        s = Salario(
            SBL=Decimal("2200000"),
            sbl_por_anio=None,
            historial_salarial=None,
        )
        r = SalarioResolver(s)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")

    def test_prioridad_3_sbl_por_anio_vacio(self):
        """sbl_por_anio={} → cae a SBL único."""
        s = Salario(SBL=Decimal("2200000"), sbl_por_anio={})
        r = SalarioResolver(s)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")


# ---------------------------------------------------------------------------
# Prioridad 2 — SBL explícito por año
# ---------------------------------------------------------------------------


class TestPrioridad2SBLPorAnio:
    """El input con ``sbl_por_anio`` resuelve por año explícito."""

    def test_prioridad_2_sbl_por_anio(self):
        s = Salario(
            SBL=Decimal("2200000"),
            sbl_por_anio={2025: Decimal("2200000"), 2026: Decimal("2400000")},
        )
        r = SalarioResolver(s)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")
        assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2400000")

    def test_prioridad_2_solo_un_anio(self):
        """Solo un año tiene entrada explícita; el otro cae a SBL."""
        s = Salario(
            SBL=Decimal("2200000"),
            sbl_por_anio={2026: Decimal("2400000")},
        )
        r = SalarioResolver(s)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")
        assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2400000")


# ---------------------------------------------------------------------------
# Prioridad 1 — historial salarial (promedio del año)
# ---------------------------------------------------------------------------


class TestPrioridad1HistorialSalarial:
    """El input con ``historial_salarial`` calcula el promedio del año."""

    def test_prioridad_1_historial_salarial_promedio_anual(self):
        s = Salario(
            SBL=Decimal("2200000"),
            historial_salarial=[
                MesValor(año=2025, mes=11, valor=Decimal("2100000")),
                MesValor(año=2025, mes=12, valor=Decimal("2300000")),
                MesValor(año=2026, mes=1, valor=Decimal("2400000")),
            ],
        )
        r = SalarioResolver(s)
        # 2025: promedio (2.100.000 + 2.300.000) / 2 = 2.200.000
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")
        # 2026: solo enero → 2.400.000
        assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2400000")

    def test_historial_sin_meses_para_anio_cae_a_sbl_por_anio(self):
        """Si el historial no tiene meses del año, cae al siguiente nivel."""
        s = Salario(
            SBL=Decimal("2200000"),
            sbl_por_anio={2026: Decimal("2400000")},
            historial_salarial=[
                MesValor(año=2025, mes=6, valor=Decimal("2300000"))
            ],
        )
        r = SalarioResolver(s)
        # 2025: promedio = 2.300.000 (único mes)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2300000")
        # 2026: historial vacío → cae a sbl_por_anio
        assert r.sbl_para_segmento(_seg(2026, 160)) == Decimal("2400000")

    def test_historial_vacio_lista(self):
        """historial_salarial=[] → cae a sbl_por_anio o SBL único."""
        s = Salario(
            SBL=Decimal("2200000"),
            sbl_por_anio={2025: Decimal("2500000")},
            historial_salarial=[],
        )
        r = SalarioResolver(s)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2500000")

    def test_historial_tiene_prioridad_sobre_sbl_por_anio(self):
        """El historial SIEMPRE gana sobre sbl_por_anio si tiene datos."""
        s = Salario(
            SBL=Decimal("2200000"),
            sbl_por_anio={2025: Decimal("3000000")},  # ignorado
            historial_salarial=[
                MesValor(año=2025, mes=11, valor=Decimal("2100000")),
                MesValor(año=2025, mes=12, valor=Decimal("2300000")),
            ],
        )
        r = SalarioResolver(s)
        assert r.sbl_para_segmento(_seg(2025, 46)) == Decimal("2200000")


# ---------------------------------------------------------------------------
# segmentar_periodo
# ---------------------------------------------------------------------------


class TestSegmentarPeriodo:
    """Tests para la función helper ``segmentar_periodo``."""

    def test_un_anio(self):
        """Periodo dentro de un solo año produce un segmento."""
        segs = segmentar_periodo(date(2025, 3, 1), date(2025, 5, 15))
        assert len(segs) == 1
        assert segs[0].anio == 2025
        assert segs[0].dias == 76  # Mar 1 → May 15 inclusive = 31+30+15 = 76

    def test_cruza_dos_anios(self):
        """Caso canónico: 2025-11-16 → 2026-06-09 produce 2 segmentos."""
        segs = segmentar_periodo(date(2025, 11, 16), date(2026, 6, 9))
        assert len(segs) == 2
        assert segs[0].anio == 2025
        assert segs[0].desde == date(2025, 11, 16)
        assert segs[0].hasta == date(2025, 12, 31)
        assert segs[0].dias == 46  # Nov 16 → Dic 31 inclusive
        assert segs[1].anio == 2026
        assert segs[1].desde == date(2026, 1, 1)
        assert segs[1].hasta == date(2026, 6, 9)
        assert segs[1].dias == 160  # Jan 1 → Jun 9 inclusive

    def test_cruza_tres_anios(self):
        """2024-12-01 → 2026-02-15 produce 3 segmentos."""
        segs = segmentar_periodo(date(2024, 12, 1), date(2026, 2, 15))
        assert len(segs) == 3
        assert segs[0].anio == 2024
        assert segs[0].dias == 31  # Dec 1-31
        assert segs[1].anio == 2025
        assert segs[1].dias == 365  # Full year 2025
        assert segs[2].anio == 2026
        assert segs[2].dias == 46  # Jan 1 → Feb 15

    def test_mismo_dia(self):
        """Periodo de un solo día produce un segmento de 1 día."""
        segs = segmentar_periodo(date(2025, 6, 15), date(2025, 6, 15))
        assert len(segs) == 1
        assert segs[0].dias == 1

    def test_fecha_corte_anterior_falla(self):
        """fecha_corte < fecha_ingreso lanza ValueError."""
        with pytest.raises(ValueError, match="fecha_corte"):
            segmentar_periodo(date(2025, 12, 1), date(2025, 1, 1))

    def test_borde_31_diciembre(self):
        """2025-12-31 → 2026-01-01 produce 2 segmentos, el 1° de 1 día."""
        segs = segmentar_periodo(date(2025, 12, 31), date(2026, 1, 1))
        assert len(segs) == 2
        assert segs[0].anio == 2025
        assert segs[0].dias == 1
        assert segs[1].anio == 2026
        assert segs[1].dias == 1

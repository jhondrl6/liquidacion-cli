"""SalarioResolver — SBL por año del segmento (Tarea 2.B-bis).

Addendum SL2630-2024: cada año calendario se liquida con el promedio
del salario de ESE año (SL2630-2024, Corte Suprema de Justicia).

Prioridad de resolución:
  1) ``historial_salarial`` → promedio del año del segmento
  2) ``sbl_por_anio[<año>]`` → SBL explícito por año
  3) ``SBL`` único (compatibilidad con v1.x / caso canónico)

.. note::
   Esta es la implementación canónica del diseño en el plan §7.2
   (Tarea 2.B-bis).  El ``SalarioResolver`` es consumido por
   ``WorkflowOrchestrator`` durante la ejecución.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List

from liquidator.contracts.input_model import Salario


# ---------------------------------------------------------------------------
# Dataclass auxiliar
# ---------------------------------------------------------------------------


@dataclass
class SegmentoCalculo:
    """Sub-rango de un contrato que cae dentro de un único año calendario.

    El motor itera sobre una lista de ``SegmentoCalculo`` y suma los
    resultados parciales para cada concepto.  Cada segmento lleva su
    propio ``sbl`` (resuelto por ``SalarioResolver``) y los
    ``params`` normativos del año correspondiente.
    """

    anio: int
    desde: date
    hasta: date
    sbl: Decimal  # rellenado por SalarioResolver
    dias: int


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------


class SalarioResolver:
    """Selecciona el SBL correcto para un segmento de cálculo.

    Uso típico::

        resolver = SalarioResolver(inp.salario)
        for seg in segmentos:
            seg.sbl = resolver.sbl_para_segmento(seg)
    """

    def __init__(self, salario: Salario) -> None:
        self._salario = salario

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def sbl_para_segmento(self, segmento: SegmentoCalculo) -> Decimal:
        """Devuelve el SBL que corresponde al año del *segmento*.

        Las tres prioridades se evalúan en orden; la primera que
        produzca un valor distinto de ``None`` gana.
        """
        # Prioridad 1 — historial mensual → promedio del año
        sbl = self._desde_historial(segmento.anio)
        if sbl is not None:
            return sbl

        # Prioridad 2 — SBL explícito por año
        sbl = self._desde_sbl_por_anio(segmento.anio)
        if sbl is not None:
            return sbl

        # Prioridad 3 — SBL único (compatibilidad v1.x)
        return self._salario.SBL

    # ------------------------------------------------------------------
    # Prioridades individuales
    # ------------------------------------------------------------------

    def _desde_historial(self, anio: int) -> Decimal | None:
        hist = self._salario.historial_salarial
        if not hist:
            return None
        meses = [m for m in hist if m.año == anio]
        if not meses:
            return None
        total = sum(m.valor for m in meses)
        return (total / Decimal(len(meses))).quantize(Decimal("1"))

    def _desde_sbl_por_anio(self, anio: int) -> Decimal | None:
        sbl_dict = self._salario.sbl_por_anio
        if sbl_dict is None:
            return None
        return sbl_dict.get(anio)


# ---------------------------------------------------------------------------
# Segmentación de periodos (helper reutilizable)
# ---------------------------------------------------------------------------


def segmentar_periodo(
    fecha_ingreso: date,
    fecha_corte: date,
) -> List[SegmentoCalculo]:
    """Parte un rango de fechas en segmentos dentro de cada año calendario.

    Cada segmento tiene ``dias`` = días INCLUSIVOS (la fecha de corte del
    segmento cuenta).  El campo ``sbl`` se deja en ``Decimal("0")`` —
    corresponde al llamante rellenarlo con ``SalarioResolver``.

    Ejemplo::

        2025-11-16 → 2026-06-09 produce 2 segmentos:
          SegmentoCalculo(anio=2025, desde=2025-11-16, hasta=2025-12-31, dias=46)
          SegmentoCalculo(anio=2026, desde=2026-01-01, hasta=2026-06-09, dias=160)
    """
    if fecha_corte < fecha_ingreso:
        raise ValueError(
            f"fecha_corte ({fecha_corte}) < fecha_ingreso ({fecha_ingreso})"
        )

    segmentos: List[SegmentoCalculo] = []
    cursor = fecha_ingreso

    while cursor <= fecha_corte:
        anio = cursor.year
        fin_de_anio = date(anio, 12, 31)
        hasta = min(fecha_corte, fin_de_anio)
        dias = (hasta - cursor).days + 1  # inclusivo

        segmentos.append(
            SegmentoCalculo(
                anio=anio,
                desde=cursor,
                hasta=hasta,
                sbl=Decimal("0"),  # rellenado por el llamante
                dias=dias,
            )
        )

        # Avanzar al primer día del año siguiente
        cursor = date(anio + 1, 1, 1)

    return segmentos

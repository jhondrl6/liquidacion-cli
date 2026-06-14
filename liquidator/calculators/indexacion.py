"""Indexacion IPC para prestaciones no pagadas oportunamente.

Tarea 2.X (Fase 2-bis, addendum SL2630-2024).
Origen: Planificacion/plan_modernizacion_v2.0_2026-06-09.md §7-bis.2.

Este modulo implementa la clase :class:`IPCIndexador`, que aplica la formula
de indexacion por IPC acumulado DANE a valores historicos:

    VA = VH * (IPC_referencia / IPC_origen)

donde:
- VH = valor historico (a la fecha de causacion/exigibilidad)
- IPC_origen = indice IPC acumulado a la fecha_origen
- IPC_referencia = indice IPC acumulado a la fecha_referencia
- VA = valor actualizado (a valor presente)

REPAROS BLOQUEANTES CERRADOS (reparos del addendum SL2630-2024):
- (a) La prescripcion de prestaciones se rige por **Art. 488 CST** (3 anos
  desde que la obligacion se hace exigible). Este modulo aplica la
  indexacion unicamente a periodos NO prescritos bajo esa norma.
- (c) Modelar IPC como indices ACUMULADOS, NO como tasas anuales.
  Defensa en profundidad: el constructor rechaza valores entre 0 y 1
  (que serian tasas anuales disfrazadas de indices).

La fuente canonica de datos es ``params/ipc_dane_mensual.json`` (generada
por ``scripts/build_ipc_index.py`` a partir de la variacion anual DANE
oficial). El JSON tiene indices mensuales en formato ``"YYYY-MM" -> Decimal``
con base 100 en 2010-01.
"""
from __future__ import annotations

import json
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

Fecha = date | str


class IPCIndexador:
    """Indexacion de valores historicos por IPC acumulado (DANE).

    La fuente de datos (params/ipc_dane_mensual.json o _anual.json) debe
    almacenar indices ACUMULADOS de precios, NO tasas anuales de inflacion.
    Si solo se dispone de inflacion anual, ejecutar ``scripts/build_ipc_index.py``
    para convertir a indice acumulado antes de invocar este indexador.

    Parameters
    ----------
    ipc_index : dict[str, Decimal | float | int]
        Mapa de claves ``"YYYY-MM"`` (preferible) o ``"YYYY"`` (anual) a
        valores de indice acumulado. Valores > 1; valores <= 1 disparan
        :class:`ValueError` (defensa contra tasas anuales disfrazadas).
    base_year : int
        Anio base del indice. Solo se usa para documentacion; el calculo
        de la razon es invariante al base_year.

    Attributes
    ----------
    data : dict[str, Decimal]
        Mapa normalizado de claves a Decimal.
    base_year : int

    Examples
    --------
    >>> idx = IPCIndexador({
    ...     "2020-02": Decimal("131.2"),
    ...     "2025-06": Decimal("168.5"),
    ... })
    >>> idx.indexar(Decimal("1000000"), "2020-02-14", "2025-06-09")
    Decimal('1284222')
    """

    def __init__(
        self,
        ipc_index: dict[str, Decimal | float | int | str],
        base_year: int = 2010,
    ) -> None:
        self.data: dict[str, Decimal] = {
            k: Decimal(str(v)) for k, v in ipc_index.items()
        }
        self.base_year = base_year
        self._validar_no_tasas()

    # ------------------------------------------------------------------
    # Validacion defensiva (reparo c del addendum SL2630-2024)
    # ------------------------------------------------------------------
    def _validar_no_tasas(self) -> None:
        """Rechaza fuentes que parezcan tasas anuales (valores entre 0 y 1)
        o que sean invalidas (negativos, NaN).

        Razon: si la fuente contiene tasas anuales (e.g. ``"2020": 0.036``
        para 3.6% de variacion anual), el calculo ``VA = VH * (tasa_ref /
        tasa_origen)`` daria resultados correctos en MAGNITUD si ambos
        indices son tasas, pero el modelo legal exige INDICES ACUMULADOS
        (base 100 en algun anio). Mezclar tasas con indices produce
        resultados sin sentido. Defensa en profundidad.

        Valores negativos tampoco son validos: un indice IPC por
        definicion crece respecto a su base, asi que ``v < 0`` o ``v == 0``
        son invaidos (0 seria "precio base" sin unidades utiles).
        """
        for clave, valor in self.data.items():
            if valor < Decimal("0"):
                raise ValueError(
                    f"Fuente IPC contiene valor {valor} en clave '{clave}' "
                    f"que es negativo. Los indices IPC son >= 0 (>= 1 si la "
                    f"base es 100 en un anio anterior a la clave)."
                )
            if Decimal("0") <= valor <= Decimal("1"):
                raise ValueError(
                    f"Fuente IPC contiene valor {valor} en clave '{clave}' "
                    f"que parece tasa anual (0 < v <= 1). "
                    f"Se requiere indice acumulado (> 1). "
                    f"Si la fuente son tasas, ejecutar "
                    f"scripts/build_ipc_index.py para convertirlas."
                )

    # ------------------------------------------------------------------
    # Constructores alternativos
    # ------------------------------------------------------------------
    @classmethod
    def from_json(cls, path: str | Path, base_year: int = 2010) -> IPCIndexador:
        """Carga un :class:`IPCIndexador` desde un JSON con indice acumulado.

        Acepta dos formatos:

        1. **Formato mensual plano** (``params/ipc_dane_mensual.json`` con
           ``indices`` como dict de ``"YYYY-MM"``):

           .. code-block:: json

              {
                "metadata": {...},
                "indices": {"2010-01": 100.0, "2010-02": 100.27, ...}
              }

        2. **Dict plano** ``{"2010-01": 100.0, ...}``.

        Parameters
        ----------
        path : str | Path
            Ruta al JSON.
        base_year : int
            Anio base (default 2010, convencion del proyecto).
        """
        p = Path(path)
        raw = json.loads(p.read_text(encoding="utf-8"))
        # Formato 1: archivo con metadata + indices
        if isinstance(raw, dict) and "indices" in raw:
            data = raw["indices"]
        else:
            # Formato 2: dict plano de claves a valores
            data = raw
        return cls(data, base_year=base_year)

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------
    def indice_para(self, fecha: Fecha) -> Decimal:
        """Devuelve el indice acumulado para una fecha.

        Preferencia:
        1. Clave mensual ``"YYYY-MM"`` (mas preciso).
        2. Clave anual ``"YYYY"`` (fallback — el indice anual es
           diciembre de ese anio por convencion del DANE).

        Raises
        ------
        KeyError
            Si la fecha no tiene indice disponible en la fuente.
        """
        if isinstance(fecha, date):
            clave_mensual = fecha.strftime("%Y-%m")
            clave_anual = str(fecha.year)
        else:
            # str. Acepta tanto "2020-02-14" como "2020-02" o "2020"
            s = str(fecha)
            if len(s) >= 7 and s[4] == "-":
                clave_mensual = s[:7]
            else:
                clave_mensual = s
            clave_anual = s[:4] if len(s) >= 4 else s

        if clave_mensual in self.data:
            return self.data[clave_mensual]
        if clave_anual in self.data:
            return self.data[clave_anual]
        raise KeyError(
            f"IPC no disponible para fecha={fecha!r} "
            f"(busque '{clave_mensual}' o '{clave_anual}'). "
            f"Claves disponibles: {len(self.data)} (rango "
            f"{min(self.data.keys())}..{max(self.data.keys())})."
        )

    def indexar(
        self,
        vh: Decimal | int | str,
        fecha_origen: Fecha,
        fecha_referencia: Fecha,
    ) -> Decimal:
        """Calcula el valor actualizado VA = VH * (IPC_ref / IPC_origen).

        Aplica a prestaciones no pagadas oportunamente (Art. 488 CST,
        SL2630-2024). NO usar inflacion anual directa como si fuera
        indice acumulado.

        Parameters
        ----------
        vh : Decimal | int | str
            Valor historico a la fecha_origen (en pesos colombianos).
        fecha_origen : date | str
            Fecha de causacion/exigibilidad de la obligacion.
        fecha_referencia : date | str
            Fecha hasta la cual se actualiza el valor (usualmente hoy
            o la fecha de pago efectivo).

        Returns
        -------
        Decimal
            VA redondeado a la unidad (peso) con ROUND_HALF_UP.

        Raises
        ------
        KeyError
            Si alguna de las fechas no tiene indice disponible.
        """
        vh_dec = Decimal(str(vh))
        ipc_origen = self.indice_para(fecha_origen)
        ipc_ref = self.indice_para(fecha_referencia)
        va = (vh_dec * ipc_ref) / ipc_origen
        return va.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


__all__ = ["IPCIndexador"]

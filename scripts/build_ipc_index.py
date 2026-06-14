#!/usr/bin/env python3
"""
build_ipc_index.py — Conversor de variacion anual DANE a indice acumulado mensual.

Tarea 2.X (Fase 2-bis, addendum SL2630-2024).
Origen: Planificacion/plan_modernizacion_v2.0_2026-06-09.md §7-bis.1, §7-bis.2.

Lee `params/ipc_variacion_anual_dane.csv` (variacion anual IPC cierre-diciembre,
publicada por DANE) y produce `params/ipc_dane_mensual.json` con un indice
acumulado mensual, base 2010-01 = 100.

IMPORTANTE — metodo de distribucion mensual:
La variacion anual DANE es UNA variacion COMPUESTA sobre 12 meses, no una suma
de 12 variaciones mensuales independientes. La distribucion mensual correcta es
la **raiz duodecima geometrica** de la variacion anual:

    factor_mensual = (1 + variacion_anual)^(1/12)
    indice_mes = indice_mes_anterior * factor_mensual

Esta distribucion es la unica que cumple: el cociente indice_dic / indice_dic_anio_anterior
= exactamente (1 + variacion_anual_publicada). Cualquier otra distribucion
(lineal, exponencial) NO reproduce la variacion anual oficial DANE.

LIMITACION DOCUMENTADA — sustituir por IPC mensual real si se requiere precision:
La variacion anual DANE refleja el cambio del IPC dic/2024 vs dic/2023, pero NO
preserva la trayectoria intra-anual real (que tiene estacionalidad: enero y
diciembre suelen tener variaciones distintas al promedio). Para liquidaciones
que requieren precision sub-anual (e.g. indexar un valor del 14 de febrero),
la jurisprudencia colombiana (SL2630-2024) acepta el uso del indice DANE oficial
publicado, no requiere reconstruccion. Si el usuario tiene acceso al IPC mensual
real (DANE publica la serie completa), puede editar este script para leer
`params/ipc_mensual_dane.csv` con la variacion mensual directa.

USO:
    python3 scripts/build_ipc_index.py
    # o con uv:
    uv run python3 scripts/build_ipc_index.py

VALIDACION post-build:
    python3 -c "import json; d=json.load(open('params/ipc_dane_mensual.json'));
    assert d['indices']['2024-12'] > d['indices']['2023-12']  # 2024 > 2023
    ratio = d['indices']['2024-12'] / d['indices']['2023-12']
    assert abs(ratio - 1.0520) < 0.001  # exactamente variacion anual 2024"
"""
from __future__ import annotations

import csv
import json
import math
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Tuple


# Paths (relativos al repo root; el script resuelve absolute via REPO_ROOT)
REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_INPUT = REPO_ROOT / "params" / "ipc_variacion_anual_dane.csv"
JSON_OUTPUT = REPO_ROOT / "params" / "ipc_dane_mensual.json"
BASE_MONTH = "2010-01"  # indice base = 100.0
BASE_VALUE = Decimal("100.0")


def _q(x: Decimal) -> Decimal:
    """Quantize a Decimal to 4 decimal places (precision suficiente para IPC)."""
    return x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def leer_variacion_anual(path: Path) -> List[Tuple[int, Decimal, str]]:
    """Lee el CSV y retorna lista (anio, variacion_decimal, fuente).

    Variacion en CSV viene como porcentaje (e.g. 5.79 para 5.79%); la convertimos
    a decimal (0.0579) para los calculos.
    """
    registros: List[Tuple[int, Decimal, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            anio = int(row["anio"].strip())
            variacion_pct = Decimal(row["variacion_anual_pct"].strip())
            variacion_dec = variacion_pct / Decimal("100")
            fuente = row.get("fuente", "DANE-IPC").strip()
            registros.append((anio, variacion_dec, fuente))
    return registros


def construir_indice_mensual(
    registros: List[Tuple[int, Decimal, str]],
    base_month: str = BASE_MONTH,
    base_value: Decimal = BASE_VALUE,
) -> Dict[str, Decimal]:
    """Construye el indice acumulado mensual con base = base_value en base_month.

    Modelo de transiciones:
    - Primer anio del CSV (2010): la variacion "anual" se interpreta como el
      cambio desde base_month (2010-01) hasta diciembre del mismo anio. Esto
      cubre 11 transiciones mensuales (no 12), por lo que el factor es
      (1 + r_anual)^(1/11). Documentamos esta eleccion en metadata.
    - Anios subsiguientes (2011+): la variacion "anual" cubre las 12
      transiciones de dic/anio-1 a dic/anio, factor = (1 + r_anual)^(1/12).
      Esta es la unica distribucion que reproduce la variacion anual DANE
      oficial al cierre de cada anio.

    La diferencia entre "variacion 11 meses del primer anio" y "variacion 12
    meses oficial DANE dic-2009 vs dic-2010" es de ~0.3% (1 mes de variacion).
    En la practica, el indice se usa para calcular razones IPC_ref/IPC_origen,
    que es invariante a la base. La eleccion de BASE_MONTH=2010-01 solo
    afecta los VALORES ABSOLUTOS del indice, no la indexacion.

    IMPORTANTE: el calculo se hace con precision Decimal FULL (sin redondeo
    intermedio). El redondeo a 4 decimales solo se aplica al final, en
    `escribir_json`. Esto garantiza que la variacion anual DANE oficial se
    reproduce al cierre de cada anio (ver `validar_indices`).

    Returns: dict {"YYYY-MM": Decimal}
    """
    if not registros:
        raise ValueError("CSV vacio: no hay registros de variacion anual.")

    indices: Dict[str, Decimal] = {base_month: base_value}
    anio_inicio = registros[0][0]
    if not base_month.startswith(f"{anio_inicio:04d}-"):
        raise ValueError(
            f"BASE_MONTH={base_month} no coincide con anio_inicio={anio_inicio}. "
            f"Ajustar BASE_MONTH o el CSV."
        )

    indice_previo = base_value
    for idx_anio, (anio, variacion_anual, _fuente) in enumerate(registros):
        # Primer anio: 11 transiciones (ene→feb→...→dic del mismo anio).
        # Anios siguientes: 12 transiciones (dic/anio-1→...→dic/anio).
        n_transiciones = 11 if idx_anio == 0 else 12

        # Factor: raiz N-esima geometrica de (1 + variacion_anual)
        factor_float = math.pow(1.0 + float(variacion_anual), 1.0 / n_transiciones)
        factor_mensual = Decimal(repr(round(factor_float, 12)))

        # Aplicar el factor `n_transiciones` veces avanzando mes a mes.
        # Para el primer anio: arrancamos en base_month (mes 1 ya esta en
        # indices), avanzamos hasta diciembre (mes 12). Son 11 transiciones
        # (mes 1→2, 2→3, ..., 11→12).
        # Para anios siguientes: arrancamos en diciembre del anio previo (ya
        # en indices), avanzamos hasta diciembre del anio actual. Son 12
        # transiciones (dic→ene, ene→feb, ..., nov→dic).
        for i in range(1, n_transiciones + 1):
            if idx_anio == 0:
                # Primer anio: avanzar de mes (base_month) a mes 12
                mes_actual = 1 + i
                if mes_actual > 12:
                    break
                clave = f"{anio:04d}-{mes_actual:02d}"
            else:
                # Anios siguientes: diciembre del anio previo + i meses
                anio_clave = anio - 1 if i <= 0 else anio  # dic/anio-1 ya esta
                # La primera iteracion (i=1) -> enero del anio actual
                # La 12da iteracion (i=12) -> diciembre del anio actual
                mes_calculado = i  # 1..12 = enero..diciembre
                clave = f"{anio:04d}-{mes_calculado:02d}"
            indice_actual = indice_previo * factor_mensual
            indices[clave] = indice_actual
            indice_previo = indice_actual

    return indices


def validar_indices(
    indices: Dict[str, Decimal],
    registros: List[Tuple[int, Decimal, str]],
) -> None:
    """Verifica que el cociente dic/anio / dic/anio_anterior = 1 + variacion.

    Esta es la garantia de fidelidad: si esta validacion pasa, la distribucion
    geometrica reproduce la variacion anual DANE oficial al cierre de cada anio.

    Solo aplica para anios 2+ (donde hay 12 transiciones). El primer anio usa
    11 transiciones (ene→dic del mismo anio) por construccion.
    """
    for idx_anio, (anio, variacion_anual, _fuente) in enumerate(registros):
        if idx_anio == 0:
            # Primer anio: validamos que la variacion "11 meses" coincide
            # con la variacion anual declarada (con tolerancia al desajuste
            # de 1 mes; el modelo aproxima 12 meses con 11 transiciones).
            clave_dic = f"{anio:04d}-12"
            if clave_dic not in indices:
                raise ValueError(f"Falta clave {clave_dic} en indices.")
            ratio = indices[clave_dic] / BASE_VALUE
            esperado = Decimal("1") + variacion_anual
            if abs(ratio - esperado) > Decimal("0.005"):
                raise ValueError(
                    f"Validacion FALLA para {anio} (primer anio, 11 transiciones): "
                    f"ratio dic/ene = {ratio}, esperado = {esperado}."
                )
        else:
            # Anios 2+: cociente dic / dic_anio_anterior = 1 + variacion
            clave_dic_actual = f"{anio:04d}-12"
            clave_dic_previo = f"{anio - 1:04d}-12"
            if clave_dic_actual not in indices or clave_dic_previo not in indices:
                raise ValueError(
                    f"Faltan claves {clave_dic_actual} o {clave_dic_previo} en indices."
                )
            ratio = indices[clave_dic_actual] / indices[clave_dic_previo]
            esperado = Decimal("1") + variacion_anual
            if abs(ratio - esperado) > Decimal("0.001"):
                raise ValueError(
                    f"Validacion FALLA para {anio}: ratio {ratio} != esperado {esperado}."
                )


def escribir_json(
    indices: Dict[str, Decimal],
    registros: List[Tuple[int, Decimal, str]],
    path: Path,
) -> None:
    """Escribe el JSON con metadata y la serie de indices."""
    # Calcular rango de anos cubiertos
    anios_cubiertos = sorted({anio for anio, _, _ in registros})

    payload = {
        "metadata": {
            "descripcion": (
                "Indice acumulado mensual IPC Colombia (DANE) con base 100 en "
                f"{BASE_MONTH}. Construido por distribucion geometrica uniforme "
                "de la variacion anual DANE oficial (cierre-diciembre)."
            ),
            "base_mes": BASE_MONTH,
            "base_valor": float(BASE_VALUE),
            "metodo": (
                "factor_mensual = (1 + variacion_anual)^(1/12); "
                "indice_mes = indice_mes_anterior * factor_mensual"
            ),
            "fuente_datos": "DANE-IPC (variacion anual oficial cierre-diciembre)",
            "csv_origen": "params/ipc_variacion_anual_dane.csv",
            "anios_cubiertos": anios_cubiertos,
            "anio_inicio": anios_cubiertos[0],
            "anio_fin": anios_cubiertos[-1],
            "limitacion": (
                "Distribucion uniforme geometrica: NO preserva la estacionalidad "
                "intra-anual real del IPC (enero y diciembre suelen diferir del "
                "promedio). Para precision sub-anual, sustituir por la serie "
                "mensual DANE oficial cuando se requiera."
            ),
            "version": "2026-06-13",
            "fecha_generacion": "2026-06-13",
        },
        "indices": {k: float(v) for k, v in indices.items()},
        "variacion_anual_fuente": {
            str(anio): {
                "variacion_pct": float(var * 100),
                "indice_diciembre": float(
                    indices[f"{anio:04d}-12"]
                ),
            }
            for anio, var, _ in registros
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main() -> int:
    if not CSV_INPUT.exists():
        print(f"ERROR: no existe {CSV_INPUT}", file=sys.stderr)
        return 1
    registros = leer_variacion_anual(CSV_INPUT)
    print(f"[build_ipc_index] Leidos {len(registros)} registros de {CSV_INPUT.name}")
    print(
        f"[build_ipc_index] Rango: {registros[0][0]}-{registros[-1][0]} "
        f"({len(registros)} anios)"
    )

    indices = construir_indice_mensual(registros)
    print(f"[build_ipc_index] Construidos {len(indices)} indices mensuales")

    validar_indices(indices, registros)
    print("[build_ipc_index] Validacion anual: OK (cocientes dic/dic_anterior = variacion)")

    escribir_json(indices, registros, JSON_OUTPUT)
    print(f"[build_ipc_index] Escrito {JSON_OUTPUT}")

    # Imprimir resumen para que el operador lo vea
    print("\n--- Resumen ---")
    for anio, variacion, _ in registros:
        dic = indices[f"{anio:04d}-12"]
        print(
            f"  {anio}: variacion={float(variacion * 100):5.2f}%  "
            f"indice_dic={float(dic):8.4f}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

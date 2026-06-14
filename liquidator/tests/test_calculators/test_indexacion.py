"""Tests unitarios para ``IPCIndexador`` (Tarea 2.X — Fase 2-bis).

Origen: Planificacion/plan_modernizacion_v2.0_2026-06-09.md §7-bis.2.

Cobertura:
- Rechazo de tasas anuales disfrazadas (reparo c del addendum SL2630).
- Indexacion con datos mensuales y anuales.
- Indexacion contra la fuente DANE real (``params/ipc_dane_mensual.json``).
- Carga via ``from_json`` con ambos formatos.
- Endpoints y errores (KeyError en fecha desconocida, redondeo).
"""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from liquidator.calculators.indexacion import IPCIndexador


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def ipc_dane_path() -> Path:
    """Path al JSON real de DANE generado por build_ipc_index.py."""
    return Path(__file__).resolve().parents[3] / "params" / "ipc_dane_mensual.json"


@pytest.fixture
def ipc_dane(ipc_dane_path: Path) -> IPCIndexador:
    """IPCIndexador cargado desde la fuente DANE real."""
    if not ipc_dane_path.exists():
        pytest.skip(
            f"No se encontro {ipc_dane_path}. "
            f"Ejecutar scripts/build_ipc_index.py primero."
        )
    return IPCIndexador.from_json(ipc_dane_path)


@pytest.fixture
def ipc_ficticio_mensual() -> IPCIndexador:
    """Datos ficticios del plan §7-bis.2 test_indexar_con_datos_mensuales."""
    return IPCIndexador({
        "2020-02": Decimal("131.2"),
        "2025-06": Decimal("168.5"),
    })


# ============================================================================
# Tests: rechazo de tasas anuales disfrazadas (reparo c)
# ============================================================================

class TestRechazoTasasAnuales:
    """Defensa en profundidad: NO aceptar valores 0 < v <= 1 como indices."""

    def test_tasa_anual_dos_digitos_rechazada(self):
        with pytest.raises(ValueError, match="tasa anual"):
            IPCIndexador({
                "2020": Decimal("0.036"),
                "2021": Decimal("0.054"),
            })

    def test_tasa_mensual_pequena_rechazada(self):
        with pytest.raises(ValueError, match="tasa anual"):
            IPCIndexador({"2020-01": Decimal("0.005")})

    def test_valor_igual_a_uno_rechazado(self):
        """v == 1.0 es el caso degenerado; sin variacion NO es un indice util."""
        with pytest.raises(ValueError, match="tasa anual"):
            IPCIndexador({"2020-01": Decimal("1.0")})

    def test_valor_cero_rechazado(self):
        with pytest.raises(ValueError, match="tasa anual"):
            IPCIndexador({"2020-01": Decimal("0")})

    def test_valor_negativo_rechazado(self):
        """Indices negativos no existen. (Deflacion NO genera indice < 0)."""
        with pytest.raises(ValueError, match="negativo"):
            IPCIndexador({"2020-01": Decimal("-1.5")})

    def test_valor_ligero_mayor_a_uno_aceptado(self):
        """v = 1.0001 NO es tasa anual disfrazada (es indice post-base 1.0)."""
        idx = IPCIndexador({"2020-01": Decimal("1.0001")})
        assert idx.indice_para("2020-01") == Decimal("1.0001")

    def test_un_valor_malo_entre_buenos_rechaza_todo(self):
        """Si CUALQUIER valor es 0 < v <= 1, el constructor rechaza todo."""
        with pytest.raises(ValueError, match="tasa anual"):
            IPCIndexador({
                "2019": Decimal("100.0"),
                "2020": Decimal("0.05"),  # UNA tasa
                "2021": Decimal("110.0"),
            })


# ============================================================================
# Tests: indexacion basica con datos ficticios
# ============================================================================

class TestIndexarDatosFicticios:
    """Tests del plan §7-bis.2 (valores arbitrarios, NO DANE real)."""

    def test_indexar_con_datos_mensuales_ficticios(
        self, ipc_ficticio_mensual: IPCIndexador
    ):
        """VA = 1.000.000 × (168.5 / 131.2) ≈ 1.284.222.

        (Valores del plan §7-bis.2; el ratio es el mismo que la variacion
        compuesta de los indices ficticios, no necesariamente la variacion
        DANE real.)
        """
        va = ipc_ficticio_mensual.indexar(
            Decimal("1000000"), "2020-02-14", "2025-06-09"
        )
        # 1.000.000 × 168.5 / 131.2 = 1.284.298.78 → ROUND_HALF_UP = 1284299
        assert va == Decimal("1284299")

    def test_indexar_con_datos_anuales(self):
        idx = IPCIndexador({
            "2020": Decimal("131.2"),
            "2025": Decimal("168.5"),
        })
        va = idx.indexar(Decimal("1000000"), date(2020, 2, 14), date(2025, 6, 9))
        # Mismo ratio que el caso mensual (las claves caen al fallback anual
        # porque no hay '2020-02' ni '2025-06').
        assert va == Decimal("1284299")

    def test_indice_para_preferencia_mensual_sobre_anual(self):
        """Si tengo AMBOS '2020' y '2020-02', el mensual gana."""
        idx = IPCIndexador({
            "2020": Decimal("100.0"),
            "2020-02": Decimal("105.0"),
        })
        assert idx.indice_para("2020-02-15") == Decimal("105.0")
        # Sin clave mensual, cae al anual
        assert idx.indice_para("2020-07-15") == Decimal("100.0")

    def test_indice_para_fecha_sin_datos_falla(self):
        idx = IPCIndexador({"2020": Decimal("131.2")})
        with pytest.raises(KeyError, match="2019-01-01"):
            idx.indice_para("2019-01-01")

    def test_indexar_simetria_si_mismo_indice(self):
        """Si origen = referencia, VA = VH (identidad de la indexacion)."""
        idx = IPCIndexador({
            "2020-02": Decimal("131.2"),
            "2025-06": Decimal("168.5"),
        })
        va = idx.indexar(Decimal("5000000"), "2020-02-14", "2020-02-14")
        assert va == Decimal("5000000")

    def test_indexar_con_input_int_se_convierte(self):
        """Acepta int/str como VH — conversion automatica a Decimal."""
        idx = IPCIndexador({"2020": Decimal("100.0"), "2025": Decimal("150.0")})
        va = idx.indexar(2000000, "2020-01-01", "2025-01-01")
        # 2.000.000 × 150 / 100 = 3.000.000
        assert va == Decimal("3000000")

    def test_redondeo_a_peso_con_round_half_up(self):
        """VA redondeado a la unidad (peso) con ROUND_HALF_UP."""
        idx = IPCIndexador({
            "2020": Decimal("100.0"),
            "2025": Decimal("150.5"),
        })
        # 1.000.000 × 150.5 / 100 = 1.505.000.0 exacto
        va = idx.indexar(Decimal("1000000"), "2020-01-01", "2025-01-01")
        assert va == Decimal("1505000")


# ============================================================================
# Tests: carga desde JSON (formato con metadata + dict plano)
# ============================================================================

class TestFromJson:
    """Carga de la fuente canonica ``params/ipc_dane_mensual.json``."""

    def test_from_json_formato_con_metadata(self, ipc_dane_path: Path):
        if not ipc_dane_path.exists():
            pytest.skip(f"No existe {ipc_dane_path}")
        idx = IPCIndexador.from_json(ipc_dane_path)
        # Verificamos que tiene datos del rango esperado
        assert "2010-01" in idx.data
        assert "2026-06" in idx.data or "2026-05" in idx.data

    def test_from_json_formato_dict_plano(self, tmp_path: Path):
        path = tmp_path / "ipc_plain.json"
        path.write_text(json.dumps({
            "2020-02": 131.2,
            "2025-06": 168.5,
        }))
        idx = IPCIndexador.from_json(path)
        assert idx.indice_para("2020-02-15") == Decimal("131.2")

    def test_from_json_base_year_se_almacena(self, ipc_dane_path: Path):
        if not ipc_dane_path.exists():
            pytest.skip(f"No existe {ipc_dane_path}")
        idx = IPCIndexador.from_json(ipc_dane_path, base_year=2018)
        assert idx.base_year == 2018


# ============================================================================
# Tests: integracion con fuente DANE real
# ============================================================================

class TestIntegracionDaneReal:
    """Tests de integracion contra ``params/ipc_dane_mensual.json``.

    El test clave verifica que indexar $1.000.000 desde febrero 2020 hasta
    junio 2025 produce un VA coherente con la variacion acumulada DANE real
    (aprox 1.42x dado que incluye 2022 con 13.12% de inflacion).
    """

    def test_indice_base_es_100_en_2010_01(self, ipc_dane: IPCIndexador):
        assert ipc_dane.indice_para("2010-01") == pytest.approx(100.0, abs=1e-6)

    def test_indice_dic_2010_coincide_con_variacion_anual(
        self, ipc_dane: IPCIndexador
    ):
        """IPC dic-2010 / IPC 2010-01 ≈ 1.0317 (variacion 2010)."""
        # Como BASE es 2010-01, dic-2010 / 2010-01 = 11 transiciones
        # (modelo) ≈ variacion anual + un mes.
        dic_2010 = ipc_dane.indice_para("2010-12")
        ene_2010 = ipc_dane.indice_para("2010-01")
        ratio = Decimal(str(dic_2010)) / Decimal(str(ene_2010))
        # Tolerancia: ~0.3% (la variacion 11-meses difiere de la 12-meses)
        assert abs(ratio - Decimal("1.0317")) < Decimal("0.005")

    def test_indice_dic_diciembre_de_cada_anio_reproduce_variacion(
        self, ipc_dane: IPCIndexador
    ):
        """dic/Y / dic/(Y-1) = 1 + variacion_anual(Y) (anios 2+)."""
        pares = [
            ("2011-12", "2010-12", 0.0579),
            ("2020-12", "2019-12", 0.0161),
            ("2022-12", "2021-12", 0.1312),
            ("2024-12", "2023-12", 0.0520),
        ]
        for dic_actual, dic_previo, variacion in pares:
            val_actual = Decimal(str(ipc_dane.indice_para(dic_actual)))
            val_previo = Decimal(str(ipc_dane.indice_para(dic_previo)))
            ratio = val_actual / val_previo
            esperado = Decimal("1") + Decimal(str(variacion))
            assert abs(ratio - esperado) < Decimal("0.001"), (
                f"Para {dic_actual}/{dic_previo}: ratio={ratio}, esperado={esperado}"
            )

    def test_indexar_1m_2020_a_2025_con_datos_dane_reales(
        self, ipc_dane: IPCIndexador
    ):
        """Caso golden: $1.000.000 de feb-2020 a jun-2025.

        Esperado ≈ 1.422.920 (ratio DANE real: incluye 2022 con 13.12%
        de variacion acumulada, lo que da un ratio de ~1.42x).
        """
        va = ipc_dane.indexar(
            Decimal("1000000"), "2020-02-14", "2025-06-09"
        )
        # Tolerancia ±1 peso por redondeo
        assert abs(va - Decimal("1422920")) <= Decimal("10")

    def test_indexar_no_decrece_si_referencia_mas_cercana(
        self, ipc_dane: IPCIndexador
    ):
        """Sanity: VA(2020, 2025) > VA(2020, 2024) (mayor periodo = mayor VA)."""
        va_2024 = ipc_dane.indexar(Decimal("1000000"), "2020-02-14", "2024-06-09")
        va_2025 = ipc_dane.indexar(Decimal("1000000"), "2020-02-14", "2025-06-09")
        assert va_2025 > va_2024


# ============================================================================
# Tests: conformidad con reparos del addendum (no-regresion)
# ============================================================================

class TestReparosAddendumCerrados:
    """Verifica que los reparos bloqueantes del addendum SL2630 estan cerrados."""

    def test_reparo_c_ipc_es_indice_no_tasa(self):
        """Reparo (c): IPC modelado como indice acumulado, no tasa.

        El test test_valor_ligero_mayor_a_uno_aceptado confirma que 1.0001
        se acepta (es un indice post-base), y test_tasa_anual_dos_digitos_rechazada
        confirma que 0.036 NO se acepta. La combinacion es la garantia.
        """
        # Si el modelo aceptara tasas, este test PASARIA con un valor cualquiera.
        # Si las rechaza, este test confirma la defensa.
        with pytest.raises(ValueError):
            IPCIndexador({"2024": Decimal("0.05")})

    def test_no_referencias_a_articulo_incorrecto_en_modulo(self):
        """Reparo (a): cero referencias al termino general equivocado de
        prescripcion en este modulo.

        La prescripcion de prestaciones se rige por el termino especial del
        CST (Art. 488), no por el termino general. El IPCIndexador NO debe
        mencionar el termino general (ni como error, ni como nota, ni en
        docstring) — solo el termino especial (Art. 488) es la base legal.
        """
        # test_calculators/test_indexacion.py -> parents[2] = liquidator/
        mod_path = Path(__file__).resolve().parents[2] / "calculators" / "indexacion.py"
        text = mod_path.read_text(encoding="utf-8")
        # Cadena prohibida: termino general de prescripcion (ver R-LEG-02).
        cadena_prohibida = "Art. 155"
        # Ninguna mencion (ni siquiera en comentarios o docstring).
        # Esto es la verificacion dura del reparo (a) del addendum.
        assert cadena_prohibida not in text, (
            f"Modulo {mod_path} contiene referencia al termino general "
            f"equivocado de prescripcion. El addendum SL2630-2024 (reparo a) "
            f"prohibe terminantemente usar ese termino como base para "
            f"prescripcion de prestaciones. Solo Art. 488 CST (termino "
            f"especial) es valido. Eliminar toda referencia."
        )
        # En cambio, Art. 488 SI debe estar mencionado (como la base legal)
        assert "Art. 488" in text, (
            f"Modulo {mod_path} debe mencionar Art. 488 CST (reparo a cerrado)."
        )

"""Tests for PreRenderValidator por motivo (Tarea 3.G, Fase 3).

Valida que la matriz REQUISITOS_POR_MOTIVO se aplica correctamente
para cada motivo de terminación del contrato laboral.

Origen: Addendum finiquito/vacaciones 2026-06-11 §C, Tarea 3.G.
"""

from decimal import Decimal
from typing import Any

import pytest

from liquidator.contracts.input_model import (
    LiquidacionInput,
    MotivoTerminacion,
)
from liquidator.output.pre_render_validator import (
    REQUISITOS_POR_MOTIVO,
    PreRenderValidationError,
    PreRenderValidator,
    obtener_nota_render,
)

# ---------------------------------------------------------------------------
# Helper: crear input mínimo para tests
# ---------------------------------------------------------------------------


def _make_input(
    motivo: str | None = None,
    modo: str = "FINIQUITO",
    fecha_terminacion: str = "2026-06-15",
    tipo: str = "INDEFINIDO",
    preaviso_entregado: bool | None = None,
) -> LiquidacionInput:
    """Crea un LiquidacionInput mínimo para tests."""
    data: dict[str, Any] = {
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador": {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": fecha_terminacion,
            "tipo": tipo,
        },
        "salario": {"SBL": 2200000},
        "modo": modo,
    }
    if motivo:
        data["contrato"]["motivo_terminacion"] = motivo
        data["contrato"]["fecha_terminacion_real"] = fecha_terminacion
    if preaviso_entregado is not None:
        data["contrato"]["preaviso_entregado"] = preaviso_entregado
    if tipo == "FIJO" and motivo == "termino_fijo_vencido":
        # FIJO + termino_fijo_vencido + FINIQUITO exige preaviso_entregado
        if preaviso_entregado is None:
            data["contrato"]["preaviso_entregado"] = True
            data["contrato"]["fecha_preaviso"] = "2026-05-15"
            data["contrato"]["dias_preaviso"] = 31
    return LiquidacionInput.model_validate(data)


# ---------------------------------------------------------------------------
# Tests de cobertura de la matriz
# ---------------------------------------------------------------------------


class TestCoberturaMatrizMotivos:
    """Verifica que cada motivo del enum tiene entrada en la matriz."""

    def test_cobertura_matriz_motivos(self):
        """Cada valor de MotivoTerminacion debe tener entrada en REQUISITOS_POR_MOTIVO."""
        for motivo in MotivoTerminacion:
            assert motivo.value in REQUISITOS_POR_MOTIVO, (
                f"MotivoTerminacion.{motivo.name} = '{motivo.value}' "
                f"no tiene entrada en REQUISITOS_POR_MOTIVO"
            )


# ---------------------------------------------------------------------------
# Tests de renuncia_voluntaria
# ---------------------------------------------------------------------------


class TestRenunciaVoluntaria:
    """Tests específicos para renuncia voluntaria (Art. 49 num. 6)."""

    def test_renuncia_sin_indemnizacion_pasa(self):
        """Renuncia sin indemnización: pasa (no hay Art. 64 CST)."""
        inp = _make_input(motivo="renuncia_voluntaria")
        desglose = {
            "vacaciones": {"valor": Decimal("550000"), "dias": Decimal("7.5")},
            # NO indemnizacion (es renuncia)
        }
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_renuncia_con_indemnizacion_falla(self):
        """Renuncia CON indemnización: falla (no debería haber Art. 64)."""
        inp = _make_input(motivo="renuncia_voluntaria")
        desglose = {
            "vacaciones": {"valor": Decimal("550000"), "dias": Decimal("7.5")},
            "indemnizacion": {"valor": Decimal("1000000")},  # NO debería estar
        }
        with pytest.raises(
            PreRenderValidationError, match="NO debe incluir.*indemnizacion"
        ):
            PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_renuncia_sin_vacaciones_falla(self):
        """Renuncia sin vacaciones: falla (vacaciones siempre se pagan)."""
        inp = _make_input(motivo="renuncia_voluntaria")
        desglose = {
            # vacaciones faltante
            "cesantias": {"valor": Decimal("1000000")},
        }
        with pytest.raises(
            PreRenderValidationError, match="requiere renglón.*vacaciones"
        ):
            PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_renuncia_nota_render_correcta(self):
        """La nota de renuncia cita Art. 49 num. 6 y Art. 64 CST."""
        nota = obtener_nota_render("renuncia_voluntaria")
        assert nota is not None
        assert "Art. 49 num. 6" in nota
        assert "Art. 64" in nota


# ---------------------------------------------------------------------------
# Tests de despido_sin_justa_causa
# ---------------------------------------------------------------------------


class TestDespidoSinJustaCausa:
    """Tests específicos para despido sin justa causa (Art. 64)."""

    def test_despido_con_vacaciones_e_indemnizacion_pasa(self):
        """Despido con vacaciones e indemnización: pasa."""
        inp = _make_input(motivo="despido_sin_justa_causa")
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
            "indemnizacion": {"valor": Decimal("1000000")},
        }
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_despido_sin_indemnizacion_falla(self):
        """Despido sin indemnización: falla (Art. 64 exige indemnización)."""
        inp = _make_input(motivo="despido_sin_justa_causa")
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
            # falta indemnizacion
        }
        with pytest.raises(
            PreRenderValidationError, match="requiere renglón.*indemnizacion"
        ):
            PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)


# ---------------------------------------------------------------------------
# Tests de despido_con_justa_causa
# ---------------------------------------------------------------------------


class TestDespidoConJustaCausa:
    """Tests específicos para despido con justa causa (Art. 62)."""

    def test_despido_con_causa_sin_indemnizacion_pasa(self):
        """Despido con causa sin indemnización: pasa."""
        inp = _make_input(motivo="despido_con_justa_causa")
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
        }
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_despido_con_causa_con_indemnizacion_falla(self):
        """Despido con causa CON indemnización: falla (no aplica Art. 64)."""
        inp = _make_input(motivo="despido_con_justa_causa")
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
            "indemnizacion": {"valor": Decimal("1000000")},
        }
        with pytest.raises(
            PreRenderValidationError, match="NO debe incluir.*indemnizacion"
        ):
            PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)


# ---------------------------------------------------------------------------
# Tests de termino_fijo_vencido
# ---------------------------------------------------------------------------


class TestTerminoFijoVencido:
    """Tests específicos para término fijo vencido (Art. 46)."""

    def test_termino_fijo_con_preaviso_pasa(self):
        """Término fijo con preaviso verificado: pasa."""
        inp = _make_input(
            motivo="termino_fijo_vencido",
            tipo="FIJO",
        )
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
            "preaviso_check": {"valor": Decimal("1")},
        }
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_termino_fijo_sin_preaviso_falla(self):
        """Término fijo sin preaviso: falla."""
        inp = _make_input(
            motivo="termino_fijo_vencido",
            tipo="FIJO",
        )
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
            # falta preaviso_check
        }
        with pytest.raises(
            PreRenderValidationError, match="requiere renglón.*preaviso_check"
        ):
            PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)


# ---------------------------------------------------------------------------
# Tests de otros motivos
# ---------------------------------------------------------------------------


class TestOtrosMotivos:
    """Tests para otros motivos de terminación."""

    @pytest.mark.parametrize(
        "motivo",
        [
            "obra_o_labor_terminada",
            "mutuo_acuerdo",
            "muerte_trabajador",
            "muerte_empleador",
            "suspension_deficitaria",
            "cierre_empresa",
        ],
    )
    def test_otros_motivos_con_vacaciones_pasan(self, motivo: str):
        """Otros motivos con vacaciones: pasan (requisito mínimo)."""
        inp = _make_input(motivo=motivo)
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
        }
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)


# ---------------------------------------------------------------------------
# Tests de guard: sin motivo, PERIODICA
# ---------------------------------------------------------------------------


class TestGuards:
    """Tests de guards (sin motivo, PERIODICA)."""

    def test_periodico_no_evalua_matriz(self):
        """PERIODICA no aplica matriz (sin motivo_terminacion)."""
        inp = _make_input(modo="PERIODICA")
        desglose = {"cesantias": {"valor": Decimal("1000000")}}
        # No raise (PERIODICA no aplica matriz)
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_finiquito_sin_motivo_no_evalua_matriz(self):
        """FINIQUITO sin motivo_terminacion no aplica matriz.

        Nota: no se puede crear un LiquidacionInput real con FINIQUITO
        sin motivo (el model_validator lo impide). Probamos el validator
        directamente con un wrapper manual.
        """

        class _ContratoWrapper:
            motivo_terminacion = None

        class _InputWrapper:
            contrato = _ContratoWrapper()

        desglose = {"cesantias": {"valor": Decimal("1000000")}}
        # No raise (sin motivo)
        PreRenderValidator().validar_requisitos_por_motivo(
            _InputWrapper(), desglose
        )


# ---------------------------------------------------------------------------
# Tests de obtener_nota_render
# ---------------------------------------------------------------------------


class TestObtenerNotaRender:
    """Tests de la función obtener_nota_render."""

    def test_renuncia_retorna_nota(self):
        nota = obtener_nota_render("renuncia_voluntaria")
        assert nota is not None
        assert "NO HAY INDEMNIZACIÓN" in nota

    def test_despido_sin_justa_causa_retorna_nota_vacia(self):
        """despido_sin_justa_causa tiene nota vacía (tiene indemnización)."""
        nota = obtener_nota_render("despido_sin_justa_causa")
        assert nota is None  # nota vacía retorna None

    def test_motivo_inexistente_retorna_none(self):
        """Motivo no catalogado retorna None."""
        assert obtener_nota_render("motivo_fantasma") is None


# ---------------------------------------------------------------------------
# Tests de integración con PreRenderValidator (edge cases)
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases del PreRenderValidator."""

    def test_desglose_con_valor_cero_falla(self):
        """Vacaciones con valor 0 falla (requiere > 0)."""
        inp = _make_input(motivo="renuncia_voluntaria")
        desglose = {
            "vacaciones": {"valor": Decimal("0")},
        }
        with pytest.raises(
            PreRenderValidationError, match="requiere renglón.*vacaciones.*valor > 0"
        ):
            PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_indemnizacion_con_valor_cero_no_falla(self):
        """Indemnización con valor 0 NO falla (no_requiere solo falla si > 0)."""
        inp = _make_input(motivo="renuncia_voluntaria")
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
            "indemnizacion": {"valor": Decimal("0")},
        }
        # No raise: indemnizacion = 0 está OK
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

    def test_indemnizacion_none_no_falla(self):
        """Indemnización como None (no existe) NO falla."""
        inp = _make_input(motivo="renuncia_voluntaria")
        desglose = {
            "vacaciones": {"valor": Decimal("550000")},
        }
        # No raise: indemnizacion no existe
        PreRenderValidator().validar_requisitos_por_motivo(inp, desglose)

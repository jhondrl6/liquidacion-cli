"""Tests de MotivoTerminacion y validación cruzada (Tarea 1.C-ter).

Cubre: enum completo, regresión canónica, finiquito con/sin motivo,
fecha_terminacion_real con/sin motivo, todos los valores del enum.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from liquidator.contracts.input_model import (
    LiquidacionInput,
    MotivoTerminacion,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_kwargs(**overrides):
    """Fixture mínimo compartido. PERIODICA, INDEFINIDO, sin motivo."""
    kwargs = {
        "trabajador": {"nombre": "X", "documento": "1"},
        "empleador": {"nombre": "Y", "documento": "2"},
        "contrato": {
            "fecha_ingreso": "2025-11-16",
            "fecha_corte": "2026-06-15",
            "tipo": "INDEFINIDO",
        },
        "salario": {"SBL": 2200000},
        "modo": "PERIODICA",
    }
    kwargs.update(overrides)
    return kwargs


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------

class TestMotivoEnum:
    """Valores del enum MotivoTerminacion."""

    def test_enum_tiene_10_valores(self):
        assert len(MotivoTerminacion) == 10

    def test_valores_canonicos(self):
        assert MotivoTerminacion.RENUNCIA_VOLUNTARIA.value == "renuncia_voluntaria"
        assert MotivoTerminacion.DESPIDO_SIN_JUSTA_CAUSA.value == "despido_sin_justa_causa"
        assert MotivoTerminacion.DESPIDO_CON_JUSTA_CAUSA.value == "despido_con_justa_causa"
        assert MotivoTerminacion.TERMINO_FIJO_VENCIDO.value == "termino_fijo_vencido"
        assert MotivoTerminacion.OBRA_O_LABOR_TERMINADA.value == "obra_o_labor_terminada"
        assert MotivoTerminacion.MUTUO_ACUERDO.value == "mutuo_acuerdo"
        assert MotivoTerminacion.MUERTE_TRABAJADOR.value == "muerte_trabajador"
        assert MotivoTerminacion.MUERTE_EMPLEADOR.value == "muerte_empleador"
        assert MotivoTerminacion.SUSPENSION_DEFICITARIA.value == "suspension_deficitaria"
        assert MotivoTerminacion.CIERRE_EMPRESA.value == "cierre_empresa"

    def test_enum_es_str(self):
        """MotivoTerminacion es str Enum → comparable con strings."""
        assert MotivoTerminacion.RENUNCIA_VOLUNTARIA == "renuncia_voluntaria"


# ---------------------------------------------------------------------------
# Regresión canónica
# ---------------------------------------------------------------------------

class TestRegresionCanonica:
    """Caso canónico PERIODICA sin vacaciones ni motivo: sigue verde."""

    def test_canonico_sin_motivo_ni_vacaciones(self):
        inp = LiquidacionInput.model_validate(_base_kwargs())
        assert inp.contrato.motivo_terminacion is None
        assert inp.contrato.fecha_terminacion_real is None
        assert inp.vacaciones is None
        assert inp.modo == "PERIODICA"

    def test_canonico_con_motivo_none_explicito(self):
        """motivo_terminacion: None explícito no rompe."""
        inp = LiquidacionInput.model_validate(_base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-15",
                "tipo": "INDEFINIDO",
                "motivo_terminacion": None,
            },
        ))
        assert inp.contrato.motivo_terminacion is None


# ---------------------------------------------------------------------------
# FINIQUITO + motivo
# ---------------------------------------------------------------------------

class TestFiniquitoConMotivo:
    """Finiquito con motivo_terminacion explícito."""

    def test_finiquito_renuncia_voluntaria_pasa(self):
        """Caso feliz: FINIQUITO por renuncia con vacaciones pendientes."""
        inp = LiquidacionInput.model_validate(_base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-15",
                "tipo": "INDEFINIDO",
                "motivo_terminacion": "renuncia_voluntaria",
                "fecha_terminacion_real": "2026-06-15",
            },
            modo="FINIQUITO",
            vacaciones={"dias_pendientes": 7.5},
        ))
        assert inp.contrato.motivo_terminacion == MotivoTerminacion.RENUNCIA_VOLUNTARIA
        assert inp.vacaciones.dias_pendientes == Decimal("7.5")

    def test_finiquito_despido_sin_justa_causa_pasa(self):
        """Finiquito por despido sin justa causa."""
        inp = LiquidacionInput.model_validate(_base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-15",
                "tipo": "INDEFINIDO",
                "motivo_terminacion": "despido_sin_justa_causa",
                "fecha_terminacion_real": "2026-06-15",
            },
            modo="FINIQUITO",
        ))
        assert inp.contrato.motivo_terminacion == MotivoTerminacion.DESPIDO_SIN_JUSTA_CAUSA

    def test_finiquito_todos_los_motivos_pasan(self):
        """Cada uno de los 10 motivos parsea correctamente en FINIQUITO."""
        for motivo in MotivoTerminacion:
            inp = LiquidacionInput.model_validate(_base_kwargs(
                contrato={
                    "fecha_ingreso": "2025-11-16",
                    "fecha_corte": "2026-06-15",
                    "tipo": "INDEFINIDO",
                    "motivo_terminacion": motivo.value,
                    "fecha_terminacion_real": "2026-06-15",
                },
                modo="FINIQUITO",
            ))
            assert inp.contrato.motivo_terminacion == motivo

    def test_finiquito_con_vacaciones_tipadas(self):
        """vacaciones como VacacionesEstado dict en FINIQUITO."""
        inp = LiquidacionInput.model_validate(_base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-15",
                "tipo": "INDEFINIDO",
                "motivo_terminacion": "renuncia_voluntaria",
                "fecha_terminacion_real": "2026-06-15",
            },
            modo="FINIQUITO",
            vacaciones={
                "dias_causados_proporcionales": 15,
                "dias_disfrutados": 0,
                "dias_pendientes": 15,
            },
        ))
        assert inp.vacaciones.dias_pendientes == Decimal("15")
        assert inp.vacaciones.dias_causados_proporcionales == Decimal("15")


class TestFiniquitoSinMotivoFalla:
    """Finiquito sin motivo_terminacion → ValidationError."""

    def test_finiquito_sin_motivo_falla(self):
        with pytest.raises(ValidationError, match="motivo_terminacion"):
            LiquidacionInput.model_validate(_base_kwargs(
                contrato={
                    "fecha_ingreso": "2025-11-16",
                    "fecha_corte": "2026-06-15",
                    "tipo": "INDEFINIDO",
                },
                modo="FINIQUITO",
            ))

    def test_finiquito_con_motivo_none_falla(self):
        with pytest.raises(ValidationError, match="motivo_terminacion"):
            LiquidacionInput.model_validate(_base_kwargs(
                contrato={
                    "fecha_ingreso": "2025-11-16",
                    "fecha_corte": "2026-06-15",
                    "tipo": "INDEFINIDO",
                    "motivo_terminacion": None,
                },
                modo="FINIQUITO",
            ))


# ---------------------------------------------------------------------------
# fecha_terminacion_real sin motivo
# ---------------------------------------------------------------------------

class TestTerminacionRealSinMotivo:
    """fecha_terminacion_real sin motivo → ValidationError."""

    def test_terminacion_real_sin_motivo_falla(self):
        with pytest.raises(ValidationError, match="motivo_terminacion"):
            LiquidacionInput.model_validate(_base_kwargs(
                contrato={
                    "fecha_ingreso": "2025-11-16",
                    "fecha_corte": "2026-06-15",
                    "tipo": "INDEFINIDO",
                    "fecha_terminacion_real": "2026-06-15",  # sin motivo
                },
            ))

    def test_terminacion_real_con_motivo_pasa(self):
        """fecha_terminacion_real CON motivo en PERIODICA pasa."""
        inp = LiquidacionInput.model_validate(_base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-15",
                "tipo": "INDEFINIDO",
                "motivo_terminacion": "renuncia_voluntaria",
                "fecha_terminacion_real": "2026-06-15",
            },
        ))
        assert inp.contrato.fecha_terminacion_real == date(2026, 6, 15)
        assert inp.contrato.motivo_terminacion == MotivoTerminacion.RENUNCIA_VOLUNTARIA


# ---------------------------------------------------------------------------
# Motivo inválido
# ---------------------------------------------------------------------------

class TestMotivoInvalido:
    """Strings que no son miembros del enum → ValidationError."""

    def test_motivo_inventado_falla(self):
        with pytest.raises(ValidationError):
            LiquidacionInput.model_validate(_base_kwargs(
                contrato={
                    "fecha_ingreso": "2025-11-16",
                    "fecha_corte": "2026-06-15",
                    "tipo": "INDEFINIDO",
                    "motivo_terminacion": "jubilacion_anticipada",  # no existe
                },
            ))

    def test_motivo_vacio_falla(self):
        with pytest.raises(ValidationError):
            LiquidacionInput.model_validate(_base_kwargs(
                contrato={
                    "fecha_ingreso": "2025-11-16",
                    "fecha_corte": "2026-06-15",
                    "tipo": "INDEFINIDO",
                    "motivo_terminacion": "",
                },
            ))

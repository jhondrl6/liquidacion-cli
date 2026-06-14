"""Tests de preaviso Art. 46 CST en Contrato (Tarea 1.C-quater, S25).

Addendum preaviso absorbido en v2.0.0. Cubre:
- Regresión dura del caso canónico PERIODICA (INDEFINIDO sin preaviso).
- Regla 1 (preaviso solo aplica a FIJO).
- Regla 2 (preaviso_entregado=True exige fecha_preaviso).
- Regla 3 (FINIQUITO+FIJO+vencido exige preaviso_entregado declarado).
- Regla 4 (otros motivos de terminación sobre FIJO NO exigen preaviso).
- Regla 5 (campos opcionales y retrocompatibles por default None).

Ver plan §6.2 Tarea 1.C-quater (línea 1271) y
Planificación/REGISTRY.md (addendum preaviso).
"""

import pytest
from datetime import date
from pydantic import ValidationError

from liquidator.contracts.input_model import (
    Contrato,
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
            "fecha_corte": "2026-06-09",
            "tipo": "INDEFINIDO",
        },
        "salario": {"SBL": 2200000},
        "modo": "PERIODICA",
    }
    kwargs.update(overrides)
    return kwargs


def _contrato_fijo_vencido_kwargs(**contrato_overrides):
    """Helper para construir kwargs con contrato FIJO+vencido por default."""
    contrato = {
        "fecha_ingreso": "2025-06-01",
        "fecha_corte": "2026-06-01",
        "tipo": "FIJO",
        "motivo_terminacion": "termino_fijo_vencido",
        "fecha_terminacion_real": "2026-06-01",
        "fecha_vencimiento_termino_fijo": "2026-06-01",
        "preaviso_entregado": True,
        "fecha_preaviso": "2026-05-01",
    }
    contrato.update(contrato_overrides)
    return _base_kwargs(
        contrato=contrato,
        modo="FINIQUITO",
    )


# ---------------------------------------------------------------------------
# 1. Regresión dura del caso canónico PERIODICA
# ---------------------------------------------------------------------------

class TestRegresionCanonica:
    """El caso canónico PERIODICA (INDEFINIDO) NO se afecta."""

    def test_canonico_periodico_sin_preaviso_sigue_verde(self):
        """Regresión dura: INDEFINIDO sin preaviso no se afecta (plan §6.2)."""
        inp = LiquidacionInput.model_validate(_base_kwargs())
        assert inp.contrato.preaviso_entregado is None
        assert inp.contrato.dias_preaviso is None
        assert inp.contrato.fecha_preaviso is None
        assert inp.contrato.fecha_vencimiento_termino_fijo is None

    def test_canonico_periodico_con_campos_preaviso_none_explicitos(self):
        """Campos de preaviso con None explícito = equivalente a omitir."""
        kwargs = _base_kwargs()
        kwargs["contrato"]["preaviso_entregado"] = None
        kwargs["contrato"]["fecha_preaviso"] = None
        kwargs["contrato"]["dias_preaviso"] = None
        kwargs["contrato"]["fecha_vencimiento_termino_fijo"] = None
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.preaviso_entregado is None

    def test_canonico_sin_campos_preaviso_no_se_pierde_motivo(self):
        """Preaviso y motivo_terminacion son independientes en PERIODICA."""
        inp = LiquidacionInput.model_validate(_base_kwargs())
        assert inp.contrato.motivo_terminacion is None
        assert inp.contrato.preaviso_entregado is None
        assert inp.modo == "PERIODICA"


# ---------------------------------------------------------------------------
# 2. Reglas de éxito: preaviso bien declarado en FIJO
# ---------------------------------------------------------------------------

class TestPreavisoReglasExito:
    """Casos felices: preaviso correctamente declarado en contrato FIJO."""

    def test_fijo_vencido_con_preaviso_pasa(self):
        """Caso feliz: FIJO + vencido + preaviso 30 días antes (plan §6.2)."""
        inp = LiquidacionInput.model_validate(_contrato_fijo_vencido_kwargs())
        assert inp.contrato.preaviso_entregado is True
        assert inp.contrato.fecha_preaviso == date(2026, 5, 1)
        assert inp.contrato.dias_preaviso is None  # no provisto
        assert inp.contrato.motivo_terminacion == MotivoTerminacion.TERMINO_FIJO_VENCIDO

    def test_fijo_vencido_con_preaviso_false_pasa(self):
        """FIJO + vencido + preaviso=False: válido (preaviso no otorgado)."""
        kwargs = _contrato_fijo_vencido_kwargs(preaviso_entregado=False)
        kwargs["contrato"].pop("fecha_preaviso", None)  # False no requiere fecha
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.preaviso_entregado is False
        assert inp.contrato.fecha_preaviso is None

    def test_fijo_vencido_con_dias_preaviso_explicitos(self):
        """El campo dias_preaviso es opcional; se acepta si se provee."""
        kwargs = _contrato_fijo_vencido_kwargs(dias_preaviso=30)
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.dias_preaviso == 30
        assert inp.contrato.preaviso_entregado is True

    def test_fijo_vencido_con_todos_los_campos_preaviso(self):
        """Todos los campos de preaviso presentes simultáneamente."""
        kwargs = _contrato_fijo_vencido_kwargs(dias_preaviso=31)
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.preaviso_entregado is True
        assert inp.contrato.fecha_preaviso == date(2026, 5, 1)
        assert inp.contrato.dias_preaviso == 31
        assert inp.contrato.fecha_vencimiento_termino_fijo == date(2026, 6, 1)


# ---------------------------------------------------------------------------
# 3. Reglas de fallo (validación cruzada)
# ---------------------------------------------------------------------------

class TestPreavisoReglasFallo:
    """Validación cruzada: preaviso mal declarado debe fallar."""

    def test_fijo_vencido_sin_preaviso_falla(self):
        """FIJO + vencido sin preaviso_entregado: ValidationError (plan §6.2)."""
        kwargs = _contrato_fijo_vencido_kwargs()
        del kwargs["contrato"]["preaviso_entregado"]
        del kwargs["contrato"]["fecha_preaviso"]
        with pytest.raises(ValidationError, match="preaviso_entregado"):
            LiquidacionInput.model_validate(kwargs)

    def test_indefinido_con_preaviso_falla(self):
        """INDEFINIDO con preaviso_entregado=True: ValidationError (plan §6.2)."""
        kwargs = _base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-09",
                "tipo": "INDEFINIDO",
                "preaviso_entregado": True,
                "fecha_preaviso": "2026-05-01",
            },
            modo="FINIQUITO",
        )
        with pytest.raises(ValidationError, match="solo aplica.*FIJO"):
            LiquidacionInput.model_validate(kwargs)

    def test_preaviso_sin_fecha_falla(self):
        """preaviso_entregado=True sin fecha_preaviso: ValidationError (plan §6.2)."""
        kwargs = _contrato_fijo_vencido_kwargs()
        del kwargs["contrato"]["fecha_preaviso"]
        with pytest.raises(ValidationError, match="fecha_preaviso"):
            LiquidacionInput.model_validate(kwargs)

    def test_obra_labor_con_preaviso_falla(self):
        """OBRA_LABOR con preaviso_entregado: falla (solo FIJO aplica)."""
        kwargs = _base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-09",
                "tipo": "OBRA_LABOR",
                "preaviso_entregado": True,
                "fecha_preaviso": "2026-05-01",
            },
            modo="FINIQUITO",
        )
        with pytest.raises(ValidationError, match="solo aplica.*FIJO"):
            LiquidacionInput.model_validate(kwargs)

    def test_prestacion_con_preaviso_falla(self):
        """PRESTACION con preaviso_entregado: falla (solo FIJO aplica)."""
        kwargs = _base_kwargs(
            contrato={
                "fecha_ingreso": "2025-11-16",
                "fecha_corte": "2026-06-09",
                "tipo": "PRESTACION",
                "preaviso_entregado": False,
            },
            modo="FINIQUITO",
        )
        with pytest.raises(ValidationError, match="solo aplica.*FIJO"):
            LiquidacionInput.model_validate(kwargs)


# ---------------------------------------------------------------------------
# 4. Consistencia: cuándo NO se exige preaviso
# ---------------------------------------------------------------------------

class TestPreavisoConsistencia:
    """Preaviso solo es obligatorio en FINIQUITO+FIJO+vencido (R2 del plan)."""

    def test_fijo_por_mutuo_acuerdo_sin_preaviso_pasa(self):
        """FIJO + mutuo_acuerdo NO exige preaviso (R2 del plan §6.2)."""
        kwargs = _base_kwargs(
            contrato={
                "fecha_ingreso": "2025-06-01",
                "fecha_corte": "2026-03-01",
                "tipo": "FIJO",
                "motivo_terminacion": "mutuo_acuerdo",
                "fecha_terminacion_real": "2026-03-01",
                # NO preaviso_entregado, NO fecha_preaviso
            },
            modo="FINIQUITO",
        )
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.motivo_terminacion == MotivoTerminacion.MUTUO_ACUERDO
        assert inp.contrato.preaviso_entregado is None

    def test_fijo_por_despido_sin_justa_causa_sin_preaviso_pasa(self):
        """FIJO + despido_sin_justa_causa NO exige preaviso."""
        kwargs = _base_kwargs(
            contrato={
                "fecha_ingreso": "2025-06-01",
                "fecha_corte": "2026-03-01",
                "tipo": "FIJO",
                "motivo_terminacion": "despido_sin_justa_causa",
                "fecha_terminacion_real": "2026-03-01",
            },
            modo="FINIQUITO",
        )
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.preaviso_entregado is None

    def test_fijo_periodico_sin_motivo_sin_preaviso_pasa(self):
        """FIJO + modo PERIODICA (sin motivo aún): preaviso es opcional."""
        kwargs = _base_kwargs(
            contrato={
                "fecha_ingreso": "2025-06-01",
                "fecha_corte": "2026-03-01",
                "tipo": "FIJO",
            },
            modo="PERIODICA",
        )
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.preaviso_entregado is None

    def test_dias_preaviso_acepta_valor_cero(self):
        """dias_preaviso=0 es válido (preaviso_entregado=True mismo día)."""
        kwargs = _contrato_fijo_vencido_kwargs(
            dias_preaviso=0,
            fecha_preaviso="2026-06-01",  # mismo día del vencimiento
        )
        inp = LiquidacionInput.model_validate(kwargs)
        assert inp.contrato.dias_preaviso == 0

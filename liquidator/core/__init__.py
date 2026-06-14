"""liquidator.core — motor de liquidación y providers."""
from liquidator.core.params_provider import ParamsProvider
from liquidator.core.salario_resolver import (
    SalarioResolver,
    SegmentoCalculo,
    segmentar_periodo,
)

__all__ = ["ParamsProvider", "SalarioResolver", "SegmentoCalculo", "segmentar_periodo"]

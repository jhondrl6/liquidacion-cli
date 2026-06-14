# liquidator/calculators/__init__.py
"""
Módulo de cálculos específicos para liquidación de nómina.
Contiene los calculadores especializados para cada concepto legal.
"""

from .indemnizacion_calculator import IndemnizacionCalculator
from .indexacion import IPCIndexador
from .prestaciones_calculator import PrestacionesCalculator
from .sbl_calculator import SBLCalculator
from .vacaciones_calculator import VacacionesCalculator

__all__ = [
    "SBLCalculator",
    "PrestacionesCalculator",
    "VacacionesCalculator",
    "IndemnizacionCalculator",
    "IPCIndexador",
]

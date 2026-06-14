"""Utilidades legales: normas, plazos, topes y recargos."""

from .normas_repository import (
    Norma,
    NormaNotFoundError,
    NormasRepository,
    NormasRepositoryError,
)
from .plazos_manager import (
    PagoFueraDePlazoError,
    PlazosManager,
    PlazosManagerError,
)
from .recargos_manager import RecargoError, RecargosManager
from .topes_manager import TopesManager

__all__ = [
    "Norma",
    "NormasRepository",
    "NormasRepositoryError",
    "NormaNotFoundError",
    "PlazosManager",
    "PlazosManagerError",
    "PagoFueraDePlazoError",
    "TopesManager",
    "RecargosManager",
    "RecargoError",
]

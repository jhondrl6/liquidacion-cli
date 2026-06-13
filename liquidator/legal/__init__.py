"""Utilidades legales: normas, plazos, topes y recargos."""

from .normas_repository import (
    Norma,
    NormasRepository,
    NormasRepositoryError,
    NormaNotFoundError,
)
from .plazos_manager import (
    PlazosManager,
    PlazosManagerError,
    PagoFueraDePlazoError,
)
from .topes_manager import TopesManager
from .recargos_manager import RecargosManager, RecargoError

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

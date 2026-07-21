"""Domain models package."""

from backend.app.domain.models.tipo_equipos import TipoEquipos
from backend.app.domain.models.subtipo_equipos import SubtipoEquipos
from backend.app.domain.models.marcas import Marcas
from backend.app.domain.models.empleados import Empleados
from backend.app.domain.models.clientes import Clientes
from backend.app.domain.models.departamentos import Departamentos
from backend.app.domain.models.equipos import Equipos
from backend.app.domain.models.equipos_subtipos import EquiposSubtipos
from backend.app.domain.models.ordenes_servicio import OrdenesServicio
from backend.app.domain.models.insumos import Insumos
from backend.app.domain.models.user import User

__all__ = [
    "TipoEquipos",
    "SubtipoEquipos",
    "Marcas",
    "Empleados",
    "Clientes",
    "Departamentos",
    "Equipos",
    "EquiposSubtipos",
    "OrdenesServicio",
    "Insumos",
    "User",
]

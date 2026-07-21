"""TipoEquipos domain model."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class TipoEquipos(Base):
    """Tipo de equipo entity."""

    __tablename__ = "tipo_equipos"

    id_tipo_equipos: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<TipoEquipos {self.nombre}>"

"""SubtipoEquipos domain model."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class SubtipoEquipos(Base):
    """Subtipo de equipo entity."""

    __tablename__ = "subtipo_equipos"

    id_subtipo: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_tipo_equipos: Mapped[int] = mapped_column(
        Integer, ForeignKey("tipo_equipos.id_tipo_equipos"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<SubtipoEquipos {self.nombre}>"

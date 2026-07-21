"""EquiposSubtipos domain model (association table for N:N)."""

from sqlalchemy import ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class EquiposSubtipos(Base):
    """Relación N:N entre Equipos y SubtipoEquipos."""

    __tablename__ = "equipos_subtipos"

    id_equipos: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("equipos.id_equipos", ondelete="CASCADE"),
        primary_key=True,
    )
    id_subtipo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subtipo_equipos.id_subtipo"),
        primary_key=True,
    )

    __table_args__ = (
        PrimaryKeyConstraint("id_equipos", "id_subtipo"),
    )

    def __repr__(self) -> str:
        return f"<EquiposSubtipos equipo={self.id_equipos} subtipo={self.id_subtipo}>"

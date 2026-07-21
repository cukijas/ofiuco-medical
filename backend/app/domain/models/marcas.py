"""Marcas domain model."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class Marcas(Base):
    """Marca entity."""

    __tablename__ = "marcas"

    id_marca: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<Marcas {self.nombre}>"

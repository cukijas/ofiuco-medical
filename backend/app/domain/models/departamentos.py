"""Departamentos domain model."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class Departamentos(Base):
    """Departamento entity."""

    __tablename__ = "departamentos"

    id_departamento: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_cliente: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id_cliente", ondelete="CASCADE"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<Departamentos {self.nombre}>"

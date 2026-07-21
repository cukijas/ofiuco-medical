"""Insumos domain model."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class Insumos(Base):
    """Insumos entity."""

    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_orden: Mapped[int] = mapped_column(
        Integer, ForeignKey("ordenes_servicio.id_orden"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_insumo: Mapped[str] = mapped_column(String(200), nullable=False)
    numero_parte: Mapped[str | None] = mapped_column(String(100), nullable=True)
    costo_unitario: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    def __repr__(self) -> str:
        return f"<Insumos {self.nombre_insumo}>"
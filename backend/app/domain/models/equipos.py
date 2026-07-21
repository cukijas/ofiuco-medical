"""Equipos domain model."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class Equipos(Base):
    """Equipo entity."""

    __tablename__ = "equipos"

    id_equipos: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_tipo_equipos: Mapped[int] = mapped_column(
        Integer, ForeignKey("tipo_equipos.id_tipo_equipos"), nullable=False
    )
    id_marca: Mapped[int] = mapped_column(
        Integer, ForeignKey("marcas.id_marca"), nullable=False
    )
    modelo: Mapped[str] = mapped_column(String(150), nullable=False)
    id_cliente: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id_cliente"), nullable=False
    )
    numero_serie: Mapped[str | None] = mapped_column(String(100), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    condicion: Mapped[str] = mapped_column(String(20), default="usado", nullable=False)
    accesorios: Mapped[str | None] = mapped_column(Text, nullable=True)
    qr_identifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    onedrive_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("condicion IN ('nuevo', 'usado', 'otro')", name="chk_condicion"),
    )

    def __repr__(self) -> str:
        return f"<Equipos {self.modelo}>"

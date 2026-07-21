"""OrdenesServicio domain model."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base


class OrdenesServicio(Base):
    """Orden de servicio entity."""

    __tablename__ = "ordenes_servicio"

    id_orden: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    numero_orden: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    numero_referencia: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    id_cliente: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id_cliente"), nullable=False
    )
    id_equipo: Mapped[int] = mapped_column(
        Integer, ForeignKey("equipos.id_equipos"), nullable=False
    )
    id_empleado: Mapped[int] = mapped_column(
        Integer, ForeignKey("empleados.id_empleado"), nullable=False
    )
    id_departamento: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departamentos.id_departamento"), nullable=True
    )
    solicitado_por: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo_visita: Mapped[str] = mapped_column(String(30), nullable=False)
    condicion_equipo: Mapped[str] = mapped_column(String(20), nullable=False)
    accesorios: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_realizacion: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_finalizacion: Mapped[date | None] = mapped_column(Date, nullable=True)
    tarea_realizada: Mapped[str | None] = mapped_column(Text, nullable=True)
    horas_trabajo: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    falla_detectada: Mapped[str | None] = mapped_column(Text, nullable=True)
    empleados_adicionales: Mapped[str | None] = mapped_column(Text, nullable=True)
    kilometros: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    viaticos: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    configuracion_equipo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    qr_identifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    onedrive_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "tipo_visita IN ('normal', 'por contrato', 'por garantia')",
            name="chk_tipo_visita",
        ),
        CheckConstraint(
            "condicion_equipo IN ('nuevo', 'usado', 'otro')",
            name="chk_condicion_orden",
        ),
    )

    def __repr__(self) -> str:
        return f"<OrdenesServicio {self.numero_orden}>"

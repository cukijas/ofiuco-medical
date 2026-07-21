"""Replace schema: drop old tables, create new ones.

Revision ID: 003
Revises: 002
Create Date: 2026-07-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop all old tables, create all new tables."""

    # === DROP OLD TABLES (reverse dependency order) ===
    op.drop_table('attachments')
    op.drop_table('service_order_parts')
    op.drop_table('service_orders')
    op.drop_table('equipment')
    op.drop_table('subcategories')
    op.drop_table('categories')
    op.drop_table('clients')
    op.drop_table('users')
    op.drop_table('onedrive_tokens')

    # === CREATE NEW TABLES (dependency order) ===

    # TipoEquipos
    op.create_table(
        'tipo_equipos',
        sa.Column('id_tipo_equipos', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('nombre', sa.String(100), nullable=False),
    )

    # SubtipoEquipos
    op.create_table(
        'subtipo_equipos',
        sa.Column('id_subtipo', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_tipo_equipos', sa.Integer(), sa.ForeignKey('tipo_equipos.id_tipo_equipos'), nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
    )

    # Marcas
    op.create_table(
        'marcas',
        sa.Column('id_marca', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('nombre', sa.String(100), nullable=False),
    )

    # Empleados
    op.create_table(
        'empleados',
        sa.Column('id_empleado', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('especialidad', sa.String(100), nullable=True),
        sa.Column('telefono', sa.String(50), nullable=True),
        sa.Column('email', sa.String(150), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Clientes
    op.create_table(
        'clientes',
        sa.Column('id_cliente', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('tipo_cliente', sa.String(20), nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('telefono', sa.String(50), nullable=True),
        sa.Column('email', sa.String(150), nullable=True),
        sa.Column('razon_social', sa.String(200), nullable=True),
        sa.Column('cuit', sa.String(20), nullable=True),
        sa.Column('obra_social', sa.String(200), nullable=True),
        sa.Column('direccion', sa.String(300), nullable=True),
        sa.Column('localidad', sa.String(100), nullable=True),
        sa.Column('dni', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("tipo_cliente IN ('fisica', 'juridica')", name='chk_tipo_cliente'),
    )

    # Departamentos
    op.create_table(
        'departamentos',
        sa.Column('id_departamento', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_cliente', sa.Integer(), sa.ForeignKey('clientes.id_cliente', ondelete='CASCADE'), nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
    )

    # Equipos
    op.create_table(
        'equipos',
        sa.Column('id_equipos', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_tipo_equipos', sa.Integer(), sa.ForeignKey('tipo_equipos.id_tipo_equipos'), nullable=False),
        sa.Column('id_marca', sa.Integer(), sa.ForeignKey('marcas.id_marca'), nullable=False),
        sa.Column('modelo', sa.String(150), nullable=False),
        sa.Column('id_cliente', sa.Integer(), sa.ForeignKey('clientes.id_cliente'), nullable=False),
        sa.Column('numero_serie', sa.String(100), nullable=True),
        sa.Column('descripcion', sa.String(500), nullable=True),
        sa.Column('condicion', sa.String(20), default='usado', nullable=False),
        sa.Column('accesorios', sa.Text(), nullable=True),
        sa.Column('qr_identifier', sa.String(255), unique=True, nullable=False),
        sa.Column('onedrive_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("condicion IN ('nuevo', 'usado', 'otro')", name='chk_condicion'),
    )

    # EquiposSubtipos (composite PK)
    op.create_table(
        'equipos_subtipos',
        sa.Column('id_equipos', sa.Integer(), sa.ForeignKey('equipos.id_equipos', ondelete='CASCADE'), nullable=False),
        sa.Column('id_subtipo', sa.Integer(), sa.ForeignKey('subtipo_equipos.id_subtipo'), nullable=False),
        sa.PrimaryKeyConstraint('id_equipos', 'id_subtipo'),
    )

    # OrdenesServicio
    op.create_table(
        'ordenes_servicio',
        sa.Column('id_orden', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('numero_orden', sa.String(10), unique=True, nullable=False),
        sa.Column('numero_referencia', sa.String(20), unique=True, nullable=False),
        sa.Column('id_cliente', sa.Integer(), sa.ForeignKey('clientes.id_cliente'), nullable=False),
        sa.Column('id_equipo', sa.Integer(), sa.ForeignKey('equipos.id_equipos'), nullable=False),
        sa.Column('id_empleado', sa.Integer(), sa.ForeignKey('empleados.id_empleado'), nullable=False),
        sa.Column('id_departamento', sa.Integer(), sa.ForeignKey('departamentos.id_departamento'), nullable=True),
        sa.Column('solicitado_por', sa.String(200), nullable=False),
        sa.Column('tipo_visita', sa.String(30), nullable=False),
        sa.Column('condicion_equipo', sa.String(20), nullable=False),
        sa.Column('accesorios', sa.Text(), nullable=True),
        sa.Column('fecha_realizacion', sa.Date(), nullable=False),
        sa.Column('fecha_finalizacion', sa.Date(), nullable=True),
        sa.Column('tarea_realizada', sa.Text(), nullable=True),
        sa.Column('horas_trabajo', sa.Numeric(5, 2), nullable=True),
        sa.Column('qr_identifier', sa.String(255), unique=True, nullable=False),
        sa.Column('onedrive_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "tipo_visita IN ('normal', 'por contrato', 'por garantia')",
            name='chk_tipo_visita',
        ),
        sa.CheckConstraint(
            "condicion_equipo IN ('nuevo', 'usado', 'otro')",
            name='chk_condicion_orden',
        ),
    )

    # === INDEXES ===
    op.create_index('idx_clientes_tipo', 'clientes', ['tipo_cliente'])
    op.create_index('idx_clientes_nombre', 'clientes', ['nombre'])
    op.create_index('idx_departamentos_cliente', 'departamentos', ['id_cliente'])
    op.create_index('idx_equipos_cliente', 'equipos', ['id_cliente'])
    op.create_index('idx_equipos_tipo', 'equipos', ['id_tipo_equipos'])
    op.create_index('idx_equipos_marca', 'equipos', ['id_marca'])
    op.create_index('idx_equipos_qr', 'equipos', ['qr_identifier'])
    op.create_index('idx_empleados_nombre', 'empleados', ['nombre'])
    op.create_index('idx_ordenes_cliente', 'ordenes_servicio', ['id_cliente'])
    op.create_index('idx_ordenes_equipo', 'ordenes_servicio', ['id_equipo'])
    op.create_index('idx_ordenes_empleado', 'ordenes_servicio', ['id_empleado'])
    op.create_index('idx_ordenes_fecha', 'ordenes_servicio', ['fecha_realizacion'])
    op.create_index('idx_ordenes_numero', 'ordenes_servicio', ['numero_referencia'])


def downgrade() -> None:
    """Drop new tables, recreate old tables."""

    # === DROP NEW TABLES (reverse dependency order) ===
    op.drop_table('ordenes_servicio')
    op.drop_table('equipos_subtipos')
    op.drop_table('equipos')
    op.drop_table('departamentos')
    op.drop_table('clientes')
    op.drop_table('empleados')
    op.drop_table('marcas')
    op.drop_table('subtipo_equipos')
    op.drop_table('tipo_equipos')

    # === RECREATE OLD TABLES (dependency order) ===

    # users
    op.create_table(
        'users',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # clients
    op.create_table(
        'clients',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(255), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('city', sa.String(255), nullable=True),
        sa.Column('province', sa.String(255), nullable=True),
        sa.Column('postal_code', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # categories
    op.create_table(
        'categories',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # subcategories
    op.create_table(
        'subcategories',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # equipment
    op.create_table(
        'equipment',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('client_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('category_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('subcategory_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('subcategories.id'), nullable=True),
        sa.Column('brand', sa.String(255), nullable=False),
        sa.Column('model', sa.String(255), nullable=False),
        sa.Column('serial_number', sa.String(255), unique=True, nullable=False),
        sa.Column('qr_code', sa.String(255), unique=True, nullable=False),
        sa.Column('onedrive_path', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # service_orders
    op.create_table(
        'service_orders',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_number', sa.String(20), unique=True, nullable=False),
        sa.Column('client_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('equipment_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('equipment.id'), nullable=False),
        sa.Column('technician_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(20), default='draft', nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('solution', sa.Text(), nullable=True),
        sa.Column('service_date', sa.Date(), nullable=True),
        sa.Column('next_service_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # service_order_parts
    op.create_table(
        'service_order_parts',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('service_order_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('service_orders.id'), nullable=False),
        sa.Column('part_name', sa.String(255), nullable=False),
        sa.Column('part_number', sa.String(255), nullable=True),
        sa.Column('quantity', sa.Integer(), default=1, nullable=False),
        sa.Column('unit_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # attachments
    op.create_table(
        'attachments',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('service_order_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('service_orders.id'), nullable=True),
        sa.Column('equipment_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('equipment.id'), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(20), nullable=False),
        sa.Column('onedrive_path', sa.String(500), nullable=True),
        sa.Column('uploaded_by', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # onedrive_tokens
    op.create_table(
        'onedrive_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

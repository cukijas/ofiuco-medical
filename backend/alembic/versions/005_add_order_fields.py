"""Add new fields to ordenes_servicio: falla_detectada, empleados_adicionales, kilometros, viaticos

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("ordenes_servicio", sa.Column("falla_detectada", sa.Text(), nullable=True))
    op.add_column("ordenes_servicio", sa.Column("empleados_adicionales", sa.Text(), nullable=True))
    op.add_column("ordenes_servicio", sa.Column("kilometros", sa.Numeric(8, 2), nullable=True))
    op.add_column("ordenes_servicio", sa.Column("viaticos", sa.Numeric(10, 2), nullable=True))

def downgrade() -> None:
    op.drop_column("ordenes_servicio", "viaticos")
    op.drop_column("ordenes_servicio", "kilometros")
    op.drop_column("ordenes_servicio", "empleados_adicionales")
    op.drop_column("ordenes_servicio", "falla_detectada")

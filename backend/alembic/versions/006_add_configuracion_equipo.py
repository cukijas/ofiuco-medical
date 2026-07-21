"""Add configuracion_equipo to ordenes_servicio

Revision ID: 006
Revises: 005
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("ordenes_servicio", sa.Column("configuracion_equipo", sa.String(50), nullable=True))

def downgrade() -> None:
    op.drop_column("ordenes_servicio", "configuracion_equipo")

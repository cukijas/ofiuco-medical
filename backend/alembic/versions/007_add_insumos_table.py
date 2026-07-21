"""Add insumos table

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "insumos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "id_orden",
            sa.Integer(),
            sa.ForeignKey("ordenes_servicio.id_orden"),
            nullable=False,
        ),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("nombre_insumo", sa.String(200), nullable=False),
        sa.Column("numero_parte", sa.String(100), nullable=True),
        sa.Column("costo_unitario", sa.Numeric(10, 2), nullable=True),
    )
    op.create_index("idx_insumos_orden", "insumos", ["id_orden"])

def downgrade() -> None:
    op.drop_index("idx_insumos_orden", table_name="insumos")
    op.drop_table("insumos")
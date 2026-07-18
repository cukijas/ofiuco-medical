"""add order fields

Revision ID: 002
Revises: 001
Create Date: 2026-07-18 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add 10 new nullable columns to service_orders."""
    op.add_column('service_orders', sa.Column('requested_by', sa.String(255), nullable=True))
    op.add_column('service_orders', sa.Column('department', sa.String(255), nullable=True))
    op.add_column('service_orders', sa.Column('visit_type', sa.String(20), nullable=True))
    op.add_column('service_orders', sa.Column('equipment_condition', sa.String(20), nullable=True))
    op.add_column('service_orders', sa.Column('declared_fault', sa.Text, nullable=True))
    op.add_column('service_orders', sa.Column('accessories', sa.Text, nullable=True))
    op.add_column('service_orders', sa.Column('work_hours', sa.Integer, nullable=True))
    op.add_column('service_orders', sa.Column('operators_count', sa.Integer, nullable=True))
    op.add_column('service_orders', sa.Column('kilometers', sa.Numeric(10, 2), nullable=True))
    op.add_column('service_orders', sa.Column('travel_expenses', sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    """Remove the 10 new columns from service_orders."""
    op.drop_column('service_orders', 'travel_expenses')
    op.drop_column('service_orders', 'kilometers')
    op.drop_column('service_orders', 'operators_count')
    op.drop_column('service_orders', 'work_hours')
    op.drop_column('service_orders', 'accessories')
    op.drop_column('service_orders', 'declared_fault')
    op.drop_column('service_orders', 'equipment_condition')
    op.drop_column('service_orders', 'visit_type')
    op.drop_column('service_orders', 'department')
    op.drop_column('service_orders', 'requested_by')

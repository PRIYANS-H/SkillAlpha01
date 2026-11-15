"""task due dates and persistent resource match cache

Revision ID: 7c1e2a9b4f10
Revises: d46448bb9265
Create Date: 2026-11-04 12:00:00

Idempotent: app startup (app.main.ensure_schema_upgrades + create_all) may already have
applied these changes on databases that were started before this migration ran.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7c1e2a9b4f10'
down_revision: Union[str, Sequence[str], None] = 'd46448bb9265'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()

    if 'roadmap_tasks' in tables:
        columns = {c['name'] for c in inspector.get_columns('roadmap_tasks')}
        if 'due_date' not in columns:
            with op.batch_alter_table('roadmap_tasks', schema=None) as batch_op:
                batch_op.add_column(sa.Column('due_date', sa.Date(), nullable=True))

    if 'resource_match_cache' not in tables:
        op.create_table(
            'resource_match_cache',
            sa.Column('cache_key', sa.String(length=255), primary_key=True),
            sa.Column('payload_json', sa.Text(), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table('resource_match_cache')
    with op.batch_alter_table('roadmap_tasks', schema=None) as batch_op:
        batch_op.drop_column('due_date')

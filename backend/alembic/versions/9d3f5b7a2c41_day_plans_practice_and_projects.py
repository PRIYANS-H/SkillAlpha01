"""day-by-day plans, breaks, practice problems and project submissions

Revision ID: 9d3f5b7a2c41
Revises: 7c1e2a9b4f10
Create Date: 2026-11-16 12:00:00

Idempotent: app startup (app.main.ensure_schema_upgrades + create_all) may already have
applied these changes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9d3f5b7a2c41'
down_revision: Union[str, Sequence[str], None] = '7c1e2a9b4f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_COLUMNS = {
    'roadmap_tasks': [
        sa.Column('kind', sa.String(length=30), nullable=True),
        sa.Column('ref_id', sa.String(length=100), nullable=True),
        sa.Column('plan_json', sa.Text(), nullable=True),
        sa.Column('steps_done', sa.Text(), nullable=True),
    ],
    'roadmaps': [
        sa.Column('study_days_per_week', sa.Integer(), nullable=True),
        sa.Column('break_until', sa.Date(), nullable=True),
    ],
}


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()

    for table, columns in NEW_COLUMNS.items():
        if table not in tables:
            continue
        existing = {c['name'] for c in inspector.get_columns(table)}
        missing = [c for c in columns if c.name not in existing]
        if missing:
            with op.batch_alter_table(table, schema=None) as batch_op:
                for column in missing:
                    batch_op.add_column(column)

    if 'problem_attempts' not in tables:
        op.create_table(
            'problem_attempts',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('problem_id', sa.String(length=60), nullable=False, index=True),
            sa.Column('attempts', sa.Integer(), nullable=True),
            sa.Column('solved', sa.Boolean(), nullable=True),
            sa.Column('self_reported', sa.Boolean(), nullable=True),
            sa.Column('points', sa.Integer(), nullable=True),
            sa.Column('solved_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )

    if 'project_submissions' not in tables:
        op.create_table(
            'project_submissions',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('project_id', sa.String(length=60), nullable=False, index=True),
            sa.Column('url', sa.Text(), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('checklist_json', sa.Text(), nullable=False),
            sa.Column('score', sa.Float(), nullable=True),
            sa.Column('submitted_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table('project_submissions')
    op.drop_table('problem_attempts')
    for table, columns in NEW_COLUMNS.items():
        with op.batch_alter_table(table, schema=None) as batch_op:
            for column in columns:
                batch_op.drop_column(column.name)

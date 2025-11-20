"""add video_id column to jobs

Revision ID: 003
Revises: 002
Create Date: 2025-11-20 11:27:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add video_id column to jobs table
    op.add_column('jobs', sa.Column('video_id', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove video_id column from jobs table
    op.drop_column('jobs', 'video_id')

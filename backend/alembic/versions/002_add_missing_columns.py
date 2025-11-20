"""Add missing columns to jobs table

Revision ID: 002
Revises: 001
Create Date: 2025-11-20 10:52:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email column to jobs table
    op.add_column('jobs', sa.Column('email', sa.String(), nullable=True))
    
    # Add completed_at column to jobs table
    op.add_column('jobs', sa.Column('completed_at', sa.DateTime(), nullable=True))
    
    # Convert status column from enum to varchar first
    op.execute("ALTER TABLE jobs ALTER COLUMN status TYPE VARCHAR")
    
    # Drop the old enum type
    op.execute("DROP TYPE IF EXISTS jobstatus")
    
    # Update existing values to new format (if any exist)
    op.execute("UPDATE jobs SET status = 'queued' WHERE status = 'PENDING'")
    op.execute("UPDATE jobs SET status = 'running' WHERE status = 'PROCESSING'")
    op.execute("UPDATE jobs SET status = 'completed' WHERE status = 'COMPLETED'")
    op.execute("UPDATE jobs SET status = 'failed' WHERE status = 'FAILED'")


def downgrade() -> None:
    op.drop_column('jobs', 'completed_at')
    op.drop_column('jobs', 'email')

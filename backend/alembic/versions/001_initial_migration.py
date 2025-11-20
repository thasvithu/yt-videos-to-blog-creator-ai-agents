"""Initial migration - create tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel_name', sa.String(), nullable=False),
        sa.Column('video_title', sa.String(), nullable=False),
        sa.Column('video_id', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='jobstatus'), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)
    
    # Create blog_posts table
    op.create_table(
        'blog_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('video_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_posts_id'), 'blog_posts', ['id'], unique=False)
    op.create_index(op.f('ix_blog_posts_job_id'), 'blog_posts', ['job_id'], unique=False)
    
    # Create embeddings table
    op.create_table(
        'embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('blog_post_id', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['blog_post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embeddings_id'), 'embeddings', ['id'], unique=False)
    op.create_index(op.f('ix_embeddings_blog_post_id'), 'embeddings', ['blog_post_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_embeddings_blog_post_id'), table_name='embeddings')
    op.drop_index(op.f('ix_embeddings_id'), table_name='embeddings')
    op.drop_table('embeddings')
    op.drop_index(op.f('ix_blog_posts_job_id'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_id'), table_name='blog_posts')
    op.drop_table('blog_posts')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
    op.execute('DROP TYPE jobstatus')
    op.execute('DROP EXTENSION IF EXISTS vector')

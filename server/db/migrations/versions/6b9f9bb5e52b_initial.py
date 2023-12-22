"""Initial migration

Revision ID: 6b9f9bb5e52b
Revises: 
Create Date: 2023-12-19 17:21:22.681351

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6b9f9bb5e52b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('org',
                    sa.Column('name', sa.String(length=30), nullable=False),
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='public'
                    )
    op.create_table('chunk',
                    sa.Column('org_id', sa.UUID(), nullable=False),
                    sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
                    sa.Column('hash_value', sa.String(length=64), nullable=False),
                    sa.Column('embedding', Vector(dim=1536), nullable=False),
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.ForeignKeyConstraint(['org_id'], ['public.org.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('org_id', 'hash_value', name='org_hash_unique_together')
                    )
    op.create_table('org_user',
                    sa.Column('user_id', sa.UUID(), nullable=False),
                    sa.Column('org_id', sa.UUID(), nullable=False),
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.ForeignKeyConstraint(['org_id'], ['public.org.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    schema='public'
                    )


def downgrade() -> None:
    op.drop_table('org_user', schema='public')
    op.drop_table('chunk')
    op.drop_table('org', schema='public')

"""Added self referencement to Scope

Revision ID: 517b8c9269c1
Revises: 8d372babce4d
Create Date: 2020-12-30 19:42:36.565353

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '517b8c9269c1'
down_revision = '8d372babce4d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('scope', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'scope', 'scope', ['parent_id'], ['id'])


def downgrade():
    op.drop_column('scope', 'parent_id')

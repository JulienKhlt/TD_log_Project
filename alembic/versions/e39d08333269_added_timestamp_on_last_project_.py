"""added timestamp on last project referencement.

Revision ID: e39d08333269
Revises: 956c57d384ec
Create Date: 2020-12-08 10:18:58.833796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e39d08333269'
down_revision = '956c57d384ec'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('last_update', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('project', 'last_update')

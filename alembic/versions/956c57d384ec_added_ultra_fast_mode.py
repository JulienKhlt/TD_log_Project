"""added ultra fast mode

Revision ID: 956c57d384ec
Revises: 572c1845132c
Create Date: 2020-11-07 23:24:24.748885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '956c57d384ec'
down_revision = '572c1845132c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('fully_indexed', sa.Boolean(), nullable=True))
    op.drop_column('project', 'onedir')

def downgrade():
    op.add_column('project', sa.Column('onedir', sa.Boolean(), nullable=True))
    op.drop_column('project', 'fully_indexed')



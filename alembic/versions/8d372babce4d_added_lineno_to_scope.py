"""Added lineno to Scope

Revision ID: 8d372babce4d
Revises: e39d08333269
Create Date: 2020-12-30 18:30:02.928237

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8d372babce4d'
down_revision = 'e39d08333269'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('scope', sa.Column('lineno', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('scope', 'lineno')

"""added reminder frequency fields

Revision ID: 0d578a14babc
Revises: 8329aaf14ffa
Create Date: 2017-12-01 17:51:34.020792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d578a14babc'
down_revision = '8329aaf14ffa'
branch_labels = None
depends_on = None


def upgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_column('scheduleevents', 'priority')
    # ### end Alembic commands ###


def downgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('scheduleevents', sa.Column('priority', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###

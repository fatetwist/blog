"""empty message

Revision ID: 4b754e76ffe5
Revises: 77f969a8abc1
Create Date: 2017-11-30 20:01:27.313714

"""

# revision identifiers, used by Alembic.
revision = '4b754e76ffe5'
down_revision = '77f969a8abc1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comments', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comments', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    # ### end Alembic commands ###
"""empty message

Revision ID: 703ca1309d72
Revises: fcbf458668b7
Create Date: 2017-12-11 08:04:23.876151

"""

# revision identifiers, used by Alembic.
revision = '703ca1309d72'
down_revision = 'fcbf458668b7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log_schcard',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip', sa.String(length=64), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('schcard_id', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('log_schcard')
    # ### end Alembic commands ###

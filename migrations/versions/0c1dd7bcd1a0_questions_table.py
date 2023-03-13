"""questions table

Revision ID: 0c1dd7bcd1a0
Revises: 1f93ea496e10
Create Date: 2023-02-09 19:19:58.372855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c1dd7bcd1a0'
down_revision = '1f93ea496e10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sub', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.drop_column('sub')

    # ### end Alembic commands ###
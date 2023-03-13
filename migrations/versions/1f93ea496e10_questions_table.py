"""questions table

Revision ID: 1f93ea496e10
Revises: 596a00cc563d
Create Date: 2023-02-09 19:18:25.588749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f93ea496e10'
down_revision = '596a00cc563d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=140), nullable=True),
    sa.Column('type', sa.String(length=20), nullable=True),
    sa.Column('yes_points', sa.Integer(), nullable=True),
    sa.Column('no_points', sa.Integer(), nullable=True),
    sa.Column('opt_points', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('questions')
    # ### end Alembic commands ###
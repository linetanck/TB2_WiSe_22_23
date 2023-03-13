"""history table

Revision ID: 596a00cc563d
Revises: 60f8749772b9
Create Date: 2023-02-09 18:30:21.275549

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '596a00cc563d'
down_revision = '60f8749772b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_history_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_history_timestamp'))

    op.drop_table('history')
    # ### end Alembic commands ###

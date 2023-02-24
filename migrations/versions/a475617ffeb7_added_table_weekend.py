"""added table weekend

Revision ID: a475617ffeb7
Revises: 6e7bda74e9e4
Create Date: 2023-02-20 14:36:37.516647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a475617ffeb7'
down_revision = '6e7bda74e9e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weekend',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('weekend', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_weekend_date'), ['date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('weekend', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_weekend_date'))

    op.drop_table('weekend')
    # ### end Alembic commands ###
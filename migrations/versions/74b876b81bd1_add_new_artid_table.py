"""Add new ArtID table

Revision ID: 74b876b81bd1
Revises: ae1ab6f9a839
Create Date: 2019-03-01 18:44:42.302957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74b876b81bd1'
down_revision = 'ae1ab6f9a839'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artid',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artname', sa.String(length=64), nullable=True),
    sa.Column('docid', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artid_artname'), 'artid', ['artname'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artid_artname'), table_name='artid')
    op.drop_table('artid')
    # ### end Alembic commands ###
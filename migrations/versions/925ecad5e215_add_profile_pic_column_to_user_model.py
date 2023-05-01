"""Add profile_pic column to User model.

Revision ID: 925ecad5e215
Revises: 8db14dbbff4a
Create Date: 2020-07-05 14:40:17.987078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '925ecad5e215'
down_revision = '8db14dbbff4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_pic', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_pic')
    # ### end Alembic commands ###
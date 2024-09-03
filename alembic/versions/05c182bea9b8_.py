"""empty message

Revision ID: 05c182bea9b8
Revises: 4b20d71259a0
Create Date: 2024-08-31 10:42:24.902906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05c182bea9b8'
down_revision: Union[str, None] = '4b20d71259a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('creator_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'creator_id')
    # ### end Alembic commands ###
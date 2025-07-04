"""new table changes

Revision ID: 59d8153c1200
Revises: 
Create Date: 2025-06-18 07:58:24.315370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59d8153c1200'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company_size',
    sa.Column('company_size_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('company_size_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('produced_product_category',
    sa.Column('product_id', sa.String(length=36), nullable=False),
    sa.Column('industry_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('details', sa.Text(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['industry_id'], ['industries.industry_id'], ),
    sa.PrimaryKeyConstraint('product_id')
    )
    op.add_column('ai_personas', sa.Column('company_size_id', sa.String(length=36), nullable=True))
    op.add_column('ai_personas', sa.Column('profile_pic', sa.String(length=255), nullable=True))

    op.create_foreign_key(None, 'ai_personas', 'company_size', ['company_size_id'], ['company_size_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ai_personas', type_='foreignkey')
    op.drop_constraint('uq_ai_persona_unique_combo', 'ai_personas', type_='unique')
    op.drop_column('ai_personas', 'profile_pic')
    op.drop_column('ai_personas', 'company_size_id')
    op.drop_table('produced_product_category')
    op.drop_table('company_size')
    # ### end Alembic commands ###

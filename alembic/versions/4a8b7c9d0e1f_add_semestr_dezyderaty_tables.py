"""add_semestr_dezyderaty_tables

Revision ID: 4a8b7c9d0e1f
Revises: 320c4ff63aa7
Create Date: 2026-03-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a8b7c9d0e1f'
down_revision: Union[str, Sequence[str], None] = '320c4ff63aa7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Tabela semestr
    op.create_table(
        'semestr',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('data_rozpoczecia', sa.Date(), nullable=False),
        sa.Column('data_zakonczenia', sa.Date(), nullable=False),
        sa.Column('nazwa', sa.String(length=100), nullable=False)
    )

    # Tabela dezyderaty
    op.create_table(
        'dezyderaty',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('data_od', sa.Date(), nullable=False),
        sa.Column('data_do', sa.Date(), nullable=False),
        sa.Column('godziny', sa.Text(), nullable=False),
        sa.Column('semestr_id', sa.Integer(), sa.ForeignKey('semestr.id', ondelete='CASCADE'), nullable=False, index=True)
    )

    # Dodaj przykładowe semestry
    op.execute("""
        INSERT INTO semestr (data_rozpoczecia, data_zakonczenia, nazwa) VALUES
        ('2025-10-01', '2026-02-28', 'Zimowy 2025/2026'),
        ('2026-03-01', '2026-06-30', 'Letni 2025/2026'),
        ('2026-10-01', '2027-02-28', 'Zimowy 2026/2027'),
        ('2027-03-01', '2027-06-30', 'Letni 2026/2027');
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('dezyderaty')
    op.drop_table('semestr')

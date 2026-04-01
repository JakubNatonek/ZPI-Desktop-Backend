"""add_album_number_to_users

Revision ID: c1d9e52ab7f4
Revises: 9b2d7e8f1a2c
Create Date: 2026-03-31 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1d9e52ab7f4"
down_revision: Union[str, Sequence[str], None] = "9b2d7e8f1a2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("album_number", sa.String(length=5), nullable=True))

    # Backfill existing users so numbering starts from 00001.
    op.execute(
        sa.text(
            """
            UPDATE users
            SET album_number = LPAD(CAST(user_id AS TEXT), 5, '0')
            WHERE album_number IS NULL
            """
        )
    )

    op.alter_column("users", "album_number", nullable=False)
    op.create_index("ix_users_album_number", "users", ["album_number"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_album_number", table_name="users")
    op.drop_column("users", "album_number")

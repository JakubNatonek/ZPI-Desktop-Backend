"""v1

Revision ID: 320c4ff63aa7
Revises: 
Create Date: 2026-03-22 12:44:21.023242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '320c4ff63aa7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Tworzenie tabel
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), unique=True, nullable=False)
    )
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), unique=True, nullable=False)
    )
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('login', sa.String(), unique=True, index=True, nullable=False),
        sa.Column('email', sa.String(), unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('plain_password', sa.String(), nullable=True),
        sa.Column('must_change_password', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('departments.id'), nullable=False)
    )
    op.create_table(
        'group',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('spec', sa.String(), nullable=False),
        sa.Column('kod', sa.String(), nullable=False),
        sa.Column('rok', sa.Integer(), nullable=False),
        sa.Column('studia', sa.String(), nullable=False)
    )
    # Tabela conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('type', sa.Enum('direct', 'group', name='conversationtypeenum'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )

    # Tabela conversation_members
    op.create_table(
        'conversation_members',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )

    # Tabela messages
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sender_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('(now() at time zone \'utc\')')),  # zbliżone do _utcnow
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Tabela alembic_version
    op.create_table(
        'alembic_version',
        sa.Column('version_num', sa.String(32), primary_key=True, nullable=False)
    )
    op.create_table(
        'teacher',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=True, index=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('prop', sa.String(), nullable=True)
    )
    op.create_table(
        'student',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False, index=True),
        sa.Column('index_number', sa.String(), unique=True, nullable=True, index=True),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('group.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('semester', sa.Integer(), nullable=True)
    )
    op.create_table(
        'subject',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('rodzaj', sa.String(), nullable=False),
        sa.Column('rodzajshow', sa.String(), nullable=True),
        sa.Column('prop_sal', sa.String(), nullable=True),
        sa.Column('zablokowany', sa.Boolean(), nullable=False, default=False),
        sa.Column('periodyczny', sa.Boolean(), nullable=False, default=False)
    )
    op.create_table(
        'room',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('building', sa.String(), nullable=False),
        sa.Column('number', sa.String(), nullable=False),
        sa.Column('seats', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('activities', sa.Text(), nullable=True)
    )
    op.create_table(
        'refresh_token_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False, index=True),
        sa.Column('jti', sa.String(), unique=True, nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Dodaj role
    op.execute("""
        INSERT INTO roles (id, name) VALUES (1, 'admin'), (2, 'Wykładowca')
        ON CONFLICT (id) DO NOTHING;
    """)
    # Dodaj department
    op.execute("""
        INSERT INTO departments (id, name) VALUES (1, 'admin'), (2, 'Informatyka'), (3, 'Fizyka')
        ON CONFLICT (id) DO NOTHING;
    """)
    # Dodaj admina
    op.execute("""
        INSERT INTO users (
            first_name, last_name, login, email, password_hash, plain_password, must_change_password, role_id, department_id
        ) VALUES (
            'admin', 'admin', 'admin', 'admin@admin.com',
            '$2b$12$zi7AdboGsbPpUp4j3qFpv.WTir3I5odeMnqzyUW4DTaN956Jq3.p.',
            NULL, FALSE, 1, 1
        )
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('refresh_token_sessions')
    op.drop_table('room')
    op.drop_table('subject')
    op.drop_table('student')
    op.drop_table('teacher')
    op.drop_table('messages')
    op.drop_table('conversation_members')
    op.drop_table('conversations')
    op.drop_table('group')
    op.drop_table('users')
    op.drop_table('departments')
    op.drop_table('roles')
    op.execute('DROP TABLE IF EXISTS alembic_version;')

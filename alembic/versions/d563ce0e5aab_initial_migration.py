"""Initial migration

Revision ID: d563ce0e5aab
Revises: 
Create Date: 2024-11-30 20:28:58.396715

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import fastapi_utils

# revision identifiers, used by Alembic.
revision = 'd563ce0e5aab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('one_to_one', 'group', 'Config', name='chattypeenum').create(op.get_bind())
    op.create_table('chat_room',
    sa.Column('id', fastapi_utils.guid_type.GUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('room_type', postgresql.ENUM('one_to_one', 'group', 'Config', name='chattypeenum', create_type=False), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', fastapi_utils.guid_type.GUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=40), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('full_name', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('chat_message',
    sa.Column('id', fastapi_utils.guid_type.GUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('attachment', sa.LargeBinary(), nullable=True),
    sa.Column('sender_id', fastapi_utils.guid_type.GUID(), nullable=True),
    sa.Column('chat_room_id', fastapi_utils.guid_type.GUID(), nullable=True),
    sa.ForeignKeyConstraint(['chat_room_id'], ['chat_room.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('room_members',
    sa.Column('chat_room_id', fastapi_utils.guid_type.GUID(), nullable=True),
    sa.Column('member_id', fastapi_utils.guid_type.GUID(), nullable=True),
    sa.ForeignKeyConstraint(['chat_room_id'], ['chat_room.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['user.id'], )
    )
    op.create_table('message_recipients',
    sa.Column('id', fastapi_utils.guid_type.GUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('receiver_id', fastapi_utils.guid_type.GUID(), nullable=True),
    sa.Column('message_id', fastapi_utils.guid_type.GUID(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('seen_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['chat_message.id'], ),
    sa.ForeignKeyConstraint(['receiver_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_recipients')
    op.drop_table('room_members')
    op.drop_table('chat_message')
    op.drop_table('user')
    op.drop_table('chat_room')
    sa.Enum('one_to_one', 'group', 'Config', name='chattypeenum').drop(op.get_bind())
    # ### end Alembic commands ###

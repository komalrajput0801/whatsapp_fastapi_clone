from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from database import Base
from core.base_models import UUIDBase

from chat.models import room_members_table

class User(UUIDBase):
    __tablename__ = "user"

    username = Column(String(20), unique=True)
    email = Column(String(40), unique=True)
    password = Column(String(100))
    is_active = Column(Boolean, default=True)
    full_name = Column(String(20), nullable=True)

    sent_messages = relationship("ChatMessage", back_populates="sender")
    received_messages = relationship("ChatMessageRecipients", back_populates="receiver")

    chats = relationship("ChatRoom", secondary=room_members_table, back_populates="members")

from datetime import datetime

from requests import session
from sqlalchemy import Column, String, Boolean, Text, Date
from sqlalchemy.orm import relationship

from chat.models import room_members_table
from core.base_models import UUIDBase
from database import Base, SessionLocal


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


class BlackListedToken(UUIDBase):
    __tablename__ = "blacklisted_token"

    token = Column(Text)
    blacklisted_at = Column(Date)

    @classmethod
    def blacklist(cls, token):
        """
        Add token to blacklist token table
        """
        session = SessionLocal()
        session.add(cls(token=token, blacklisted_at=datetime.now()))
        session.commit()

    @classmethod
    def check_token_is_blacklisted_or_not(cls, token: str):
        session = SessionLocal()
        token = session.query(cls).filter(cls.token == token)
        return token
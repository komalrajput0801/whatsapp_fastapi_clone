import enum

from fastapi_utils.guid_type import GUID

from sqlalchemy import Integer, Column, String, Text, DateTime, LargeBinary, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship

from database import Base

from core.base_models import UUIDBase

room_members_table = Table(
    "room_members",
    Base.metadata,
    Column("chat_room_id", GUID , ForeignKey("chat_room.id")),
    Column("member_id", GUID, ForeignKey("user.id"))
)


class ChatTypeEnum(str, enum.Enum):
    one_to_one = "One To One Chat"
    group = "Group Chat"

    class Config:  
        use_enum_values = True # add this line, in case when saving enum value to DB, it is taking 
                               # "One To One Chat" and not "one_to_one" and you are getting
                               # invalid representation error, make sure you migrate after this


# for now, not considering leaving and joining group
class ChatRoom(UUIDBase):
    __tablename__ = "chat_room"

    name = Column(String, unique=True)
    room_type = Column(Enum(ChatTypeEnum))
    members = relationship("User", secondary=room_members_table, back_populates="chats")

    chat_messages = relationship("ChatMessage", back_populates="chat_room")


class ChatMessage(UUIDBase):
    __tablename__ = "chat_message"

    message = Column(Text)
    sent_at = Column(DateTime)
    attachment = Column(LargeBinary)

    sender_id = Column(GUID, ForeignKey("user.id"))

    # when user is deleted, all its messages are also deleted
    sender = relationship("User", back_populates="sent_messages", cascade="all, delete")

    chat_room_id = Column(GUID, ForeignKey("chat_room.id")) # here group is the table name
    chat_room = relationship("ChatRoom", back_populates="chat_messages", cascade="all, delete")

    recipients = relationship("ChatMessageRecipients", back_populates="message")

class ChatMessageRecipients(UUIDBase):
    __tablename__ = "message_recipients"

    receiver_id = Column(GUID, ForeignKey("user.id"))
    receiver = relationship("User", back_populates="received_messages", cascade="all, delete")

    message_id = Column(GUID, ForeignKey("chat_message.id"))
    message = relationship("ChatMessage", back_populates="recipients", cascade="all, delete")

    delivered_at = Column(DateTime)
    seen_at = Column(DateTime)


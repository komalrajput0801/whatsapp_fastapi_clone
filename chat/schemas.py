from datetime import datetime

import uuid
from typing import NewType, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal
from chat.models import ChatTypeEnum, ChatRoom
from user.models import User
from user.schemas import UserOut

RoomID = NewType("RoomID", uuid.UUID)
UserID = NewType("UserID", uuid.UUID)


class ChatRoomIn(BaseModel):
    name: str
    room_type: ChatTypeEnum
    members: List[UserID]

    class Config:
        allow_population_by_field_name  = True


class ChatRoomOut(ChatRoomIn):
    id: RoomID
    members: List[UserOut]

    class Config:
        orm_mode = True

class ChatMessageIn(BaseModel):
    message: str
    chat_room_id: RoomID

    class Config:
        orm_mode = True

class ChatMessageOut(ChatMessageIn):
    sender: UserOut
    sent_at: Optional[datetime]

    # another option is to use computed_field in pydantic 2 but rust is needed to install for that
    # also we can use separate package of pydantic-computed
    @property
    def receiver(self):
        with SessionLocal() as db_session:
            chat_room = db_session.get(ChatRoom, self.chat_room_id)
            if chat_room and chat_room.room_type == ChatTypeEnum.one_to_one:
                sender = db_session.get(User, self.sender.id)
                members = chat_room.members
                members.remove(sender)
                return [UserOut.from_orm(member) for member in members]
        return []

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["receiver"] = self.receiver
        return data

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
        }
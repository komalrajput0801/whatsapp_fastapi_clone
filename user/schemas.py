# includes pydantic models
import uuid
from typing import NewType, Optional

from pydantic import BaseModel, EmailStr, constr

UserID = NewType("UserID", uuid.UUID)

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str


# model with fields needed at time of creation
class UserIn(UserBase):
    password: constr()


# model with fields at time of reading data
class UserOut(UserBase):
    id: UserID
    is_active: bool
    chat_room_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: str


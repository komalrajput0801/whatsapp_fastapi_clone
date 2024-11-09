from datetime import datetime
from uuid import UUID
from typing import List

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from chat.exceptions import RoomAlreadyExists, RoomNotFound
from chat.models import *
from chat.schemas import ChatMessageIn, ChatMessageOut, ChatRoomIn, ChatRoomOut
from user.models import User

from core.base_crud import CRUDBase
from core.dependencies import get_db

class ChatMessageCRUD(CRUDBase[ChatMessage, ChatMessageIn, ChatMessageOut]):
    def create_chat(self, user, room_id: UUID, message: str, db_session: Session):
        chat_obj = ChatMessage(
            sender=user, 
            chat_room_id=room_id, 
            message=message,
            sent_at=datetime.now()
        )
        db_session.add(chat_obj)
        db_session.flush()
        chat_msg = db_session.query(
            self.model).options(joinedload(
                self.model.sender)).filter_by(id=chat_obj.id).first()

        # add receiver of this chat message
        chat_room = db_session.get(ChatRoom, room_id)
        members = chat_room.members.copy()
        members.remove(user)
        for recipient in members:
            rec_obj = ChatMessageRecipients(
                receiver=recipient,
            )
            # TODO: need to set delivered at when message is sent to users
            chat_obj.recipients.append(rec_obj)
        db_session.commit()
        return chat_msg

    def get_chats_by_room_id(self, room_id: UUID):
        """
        Returns all chats of user of particular room id which can either be one to one or group
        """
        # TODO: use session in arguments here as well
        with SessionLocal() as db_session:
            # joinedload works same as select related in django
            return db_session.query(self.model).options(
                joinedload(self.model.sender)).filter_by(
                chat_room_id=room_id).order_by(ChatMessage.sent_at).all()

    def get_chats_by_user_id(self, user_id: UUID):
        """
        Returns all chats of user either as sender or receiver
        """
        # TODO: use session in arguments here as well
        from sqlalchemy.orm import aliased
        with SessionLocal() as db_session:
            # Aliasing the model for the correlated subquery, this is used 
            # when we will be using same model multiple times in same query
            sub_model = aliased(self.model) 

            # filter only those messages in which logged in users is sender/receiver
            base_query = db_session.query(self.model).join(ChatRoom).join(
                room_members_table).filter(room_members_table.c.member_id == user_id)

            # Query to get the most recent messages without using join
            recent_msgs = base_query.options(
                joinedload(self.model.sender), 
                joinedload(self.model.chat_room)).filter(
                self.model.sent_at == db_session.query(
                    func.max(sub_model.sent_at)).filter(
                    sub_model.chat_room_id == self.model.chat_room_id
                    ).scalar_subquery()).all()
            return recent_msgs


class ChatRoomCRUD(CRUDBase[ChatRoom, ChatRoomIn, ChatRoomOut]):
    def get_users(self, db: Session, ids: List[UUID]):
        return db.query(User).filter(User.id.in_(ids)).all()

    def create(self, db: Session, obj_in: ChatRoomIn) -> ChatRoom:
        try:
            members = self.get_users(db, obj_in.members)
            obj_in_data = jsonable_encoder(obj_in, exclude=["members"])
            chat_room_obj = self.model(**obj_in_data)
            chat_room_obj.members = members
            db.add(chat_room_obj)
            db.commit()
            db.refresh(chat_room_obj)
            return chat_room_obj
        except IntegrityError:
            db.rollback()
            raise RoomAlreadyExists()
        return chat_obj

    def add_member_to_room(self, db: Session, room_id: UUID, member_ids: List[UUID]):
        room_obj = db.query(ChatRoom).filter(ChatRoom.id == room_id)
        if not room_obj:
            raise RoomNotFound()
        members = self.get_users(member_ids)
        room_obj.members = members
        db.add(room_obj)
        db.commit()
        return room_obj

chats = ChatMessageCRUD(ChatMessage)
chat_room = ChatRoomCRUD(ChatRoom)
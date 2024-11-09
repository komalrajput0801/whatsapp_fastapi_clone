from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session

from database import SessionLocal
from core.dependencies import get_db
from chat.schemas import ChatRoomOut, ChatRoomIn, ChatMessageOut
from user.models import User
from user.utils import get_current_user
from chat.crud import chats, chat_room

router = APIRouter()
room_router = APIRouter()

# @cbv(router)
# class OneToOneChatRoom:
# 	session: Session = Depends(get_db)

# 	@router.post("/room", response_model=ChatRoomOut)
# 	# chat room is virtual space when users can exchange messages, it can be one to one as well
# 	# as group chat
# 	def create_chat_room(self, chat_room: ChatRoomIn):
# 		# TODO: need to figure out how will the room id linked to various websocket connections


# Go to chats listing
# There are no chats, select one user with whom you want to begin chatting
# Once user is selected, we create a room between both the users, that means a websocket connections
# is opened and a room is created, self.rooms[room_id] --> we add that webocket connection
# so whenever room is created, websocket connection has also to be opened up.


# now on the other side, second user will see list of chats, which will be the room id
# when he clicks on room id, a new websocket connection is opened and linked to room_connections
# is it necessary to have websocket connection when creating room ?

# it is not necessary but now the question is websocket connections should be room specific or user
# specific, as ideally it should be room specific, but what about handling of multiple notifications
# , in that case how it is managed

# we create a separate websocket endpoint for notifications

# consumers in django are same as websocket_endpoint or connection manager that we create in fastapi

# so we will be having room based connection manager that would associate websocket connections
# with room, and room creation would be separate api not handling websocket connections

# main logic flows from send and receive and based on type parameter in data, we can have different
# functions like leave group, send message, join group

@cbv(room_router)
class ChatRoomCBV:
	session: Session = Depends(get_db)
	logged_in_user: User = Depends(get_current_user)

	@room_router.post("/", response_model=ChatRoomOut)
	def create(self, room: ChatRoomIn):
		# chat room is virtual space when users can exchange messages, it can be one to one as well 
		# as group chat
		# TODO: add validation to allow only two members for one to one chat
		
		# TODO: whenever a chat room is created add its members as well which will be done by members key
		return chat_room.create(self.session, room)


@cbv(router)
class ChatCBV:
	session: Session = Depends(get_db)
	logged_in_user: User = Depends(get_current_user)

	@router.get("/{room_id}", response_model=List[ChatMessageOut])
	def get_chats_by_room_id(self, room_id: UUID):
		"""
		Returns all chat messages of particular room id
		"""
		# TODO: add validation to check if logged in user is member of room id
		return chats.get_chats_by_room_id(room_id)


	@router.get("/", response_model=List[ChatMessageOut])
	def get_chats_by_user_id(self):
		"""
		Returns all chats with recent messages in each list to show in listing 
		"""
		return chats.get_chats_by_user_id(self.logged_in_user.id)

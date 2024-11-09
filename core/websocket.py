import asyncio

from datetime import datetime

import json
import redis

from fastapi import WebSocket

from chat.crud import chats
from sqlalchemy.orm import Session
from user.models import User
from user.utils import get_users_with_room


class RedisPubSubManager:
    def __init__(self):
        try:
            # Initialize the Redis client and Pub/Sub object
            self.redis_client = redis.StrictRedis(
                host="127.0.0.1", port=6379, decode_responses=True,
                socket_timeout=5
            )
            self.pub_sub = self.redis_client.pubsub()
        except redis.exceptions.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def publish(self, channel_name: str, message: str):
        try:
            await self.redis_client.publish(channel_name, message)
        except redis.exceptions.ConnectionError as e:
            print(f"Failed to publish message: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def subscribe(self, channel_name: str):
        try:
            await self.pub_sub.subscribe(channel_name)
        except redis.exceptions.ConnectionError as e:
            print(f"Failed to subscribe to channel: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def unsubscribe(self, channel_name: str):
        try:
            await self.pub_sub.unsubscribe(channel_name)
        except redis.exceptions.ConnectionError as e:
            print(f"Failed to unsubscribe from channel: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


# check how will this whole class implemented in django channels after completion
class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections = {}

        # need to think if this is not duplicating storing connections
        # mapping
        self.user_connections = {}
        self.pubsub_client = RedisPubSubManager()

    async def listen_for_updates(self):
        for message in self.pubsub_client.pub_sub.listen():
            print("Data Received::::::;", message)

            if message["type"] == "message":
                print("Message received::::::;", message)
                # fetch user from message
                user_id = message["channel"].split(":", 1)[0]
                # confusing here as to whom send the message of online or offline
                # send messages to all user connections, this can be used for notifications also
                for websocket in self.active_connections[user_id]:
                    await websocket.send_json(data)

    async def connect(self, room_id: str, websocket: WebSocket, user: User):
        await websocket.accept()
        if room_id in self.active_connections.keys():
            self.active_connections[room_id].append(websocket)
        else:
            self.active_connections[room_id] = [websocket]

        if user.id in self.user_connections.keys():
            self.user_connections[user.id].append(websocket)
        else:
            self.user_connections[user.id] = [websocket]
        print(f"New connection added to chat room with {room_id}")
        print(f"New connection added to user {user}")

        # subscribe to all channels of chat rooms to which user is part of
        # Ideally if I have a websocket connection open, then why will I need to subscribe
        # for all the users, as a single connection tells that it is chat between two users
        # chat specific to that room id only
        users = get_users_with_room(user)
        for u in users:
            self.pubsub_client.pub_sub.subscribe(f"user:{u.id}:status")

            print(f"User {user.email} is listening for {u.email}'s status updates")
            # what create_task does is schedules coroutine to event loop as soon as possible
            # this is because if we dont use create_task, asynchronous code is written, but
            # can't run it concurrently
            # https://www.pythontutorial.net/python-concurrency/python-asyncio-create_task/
            
            # TODO: is this necessary for each, as doing it once would work i guess
            asyncio.create_task(self.listen_for_updates())

        # need to consider here the case when user is online from multiple devices
        # in that case maintain something like counter
        self.pubsub_client.redis_client.publish(f"user:{user.id}:status", "online")
        print(f"Published message that {user.email} is online")

    async def send_chat_message(self, sender: User, room_id: str, message: str, db_session: Session):
        # create chat message object and send message to all open
        # websocket connections of sender as well send message to all receivers
        # as websocket connections would be of sender and receivers both, so message 
        # would be sent to all
        chat_obj = self.add_message_to_room(sender, room_id, message, db_session)
        data = {
            "sender_id": str(chat_obj.sender_id),
            "message": chat_obj.message,
            "sent_at": chat_obj.sent_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        if room_id in self.active_connections.keys():
            for websocket in self.active_connections[room_id]:
                await websocket.send_json(data)

    async def disconnect(self, websocket: WebSocket):
        for room_id, websocket_conn in self.active_connections.items():
            if websocket in websocket_conn:
                websocket_conn.remove(websocket)
                self.active_connections[room_id] = websocket_conn

        self.pubsub_client.redis_client.publish(f"user:{user_id}:status", "offline")
        print(f"Published message that {user_id} is offline")


    def add_message_to_room(self, user, room_id, message, db_session):
        return chats.create_chat(user, room_id, message, db_session)



# do write why this approach was not used and pub sub model was used
# TODO: need to understand if two manager classes are actually needed
# class UserWebSocketConnectionManager:
#     def __init__(self):
#         self.user_connections = {}
        

#     async def connect(self, user_id: str, websocket: WebSocket):
#         await websocket.accept()

#         # need to consider here the case when user is online from multiple devices
#         # in that case maintain something like counter
#         self.pubsub_client.redis_client.publish(f"user:{user_id}:status", "online")
#         print(f"Published message that {user_id} is online")

#     async def disconnect(self, websocket: WebSocket):
#         self.pubsub_client.redis_client.publish(f"user:{user_id}:status", "offline")
#         print(f"Published message that {user_id} is offline")

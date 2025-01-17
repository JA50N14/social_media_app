import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async, aclose_old_connections
from . models import Chat, Message, ChatViewed
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
import asyncio
import redis.asyncio as aioredis


r = aioredis.Redis(host='localhost', port=6379, decode_responses=True)

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_group_id = self.scope["url_route"]["kwargs"]["chat_group_id"]
        self.chat_group_name = f'chat_{self.chat_group_id}'

        #Add channel to channel group. self.channel_name is automatically generated when a Consumer instance is instiantiated
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.accept()

        await r.hset(str(self.chat_group_name), mapping={str(self.scope["user"].username): str(self.scope["user"].username)})

        self.keep_alive_task = asyncio.create_task(self.keep_alive())


#Receive from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if message == "pong":
            return
        else:
            sender = self.scope["user"].username
            chat_with_id = text_data_json["chat_with_id"]
            chat_with_username = text_data_json["chat_with_username"]

            await aclose_old_connections()
            await self.send_to_database(message, chat_with_id)
            await self.channel_layer.group_send(self.chat_group_name, {"type": "chat.message", "message": message, "sender": sender})
            
            chat_with_in_chat_room = await r.hexists(str(self.chat_group_name), str(chat_with_username))
            if chat_with_in_chat_room:
                await self.update_chat_viewed(chat_with_id)


#Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        await self.send(text_data=json.dumps({"message": message, "sender": sender}))


    @database_sync_to_async
    def send_to_database(self, message, chat_with_id):
        sender = self.scope["user"]
        receiver = User.objects.get(id=chat_with_id)
        if sender.id < receiver.id:
            chat = Chat.objects.get(user1=sender.id, user2=receiver.id)
        else:
            chat = Chat.objects.get(user1=receiver.id, user2=sender.id)
        message_obj = Message.objects.create(chat=chat, sender=sender, content=message)
        message_obj.save()


    async def disconnect(self, close_code):
        #Leave chat group
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        await r.hdel(str(self.chat_group_name), str(self.scope["user"].username))
        
        if hasattr(self, "keep_alive_task"):
            self.keep_alive_task.cancel()


    async def keep_alive(self):
        while True:
            try:
                await self.send(text_data=json.dumps({"message": "ping"}))
                await asyncio.sleep(30)
            except:
                await self.disconnect(1000)
                break


    @database_sync_to_async
    def update_chat_viewed(self, chat_with_id):
        User = get_user_model()
        chat_with_user = get_object_or_404(User, pk=chat_with_id)
        sender = self.scope["user"]
        chat = Chat.objects.get(Q(user1=sender, user2=chat_with_user) | Q(user1=chat_with_user, user2=sender))
        ChatViewed.objects.filter(user=chat_with_user, chat=chat).update(last_viewed=timezone.now())
        chat_viewed_object = ChatViewed.objects.get(user=chat_with_user, chat=chat)

#You need to track users in each channel group - Try using redis directly
    #Check if a dictionary with the self.chat_group_name exists
        #If yes, see if self.scope["user"].username is in it
            #if yes, do nothing. Will leverage this to update ChatViewed
            #if no, add str(self.scope["user"].username) to the self.chat_group_name key
        #If no, add the self.chat_group_name as a key to the dict AND add the users username as a value
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from . models import Chat, Message, ChatGroupCurrentUserCount, ChatViewed
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
import asyncio

# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.chat_group_id = self.scope["url_route"]["kwargs"]["chat_group_id"]
#         self.chat_group_name = f'chat_{self.chat_group_id}'

#         #Add channel to channel group. self.channel_name is automatically generated when a Consumer instance is instiantiated
#         await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
#         await self.accept()

#         await self.increase_chat_group_count(self.chat_group_name)

#         self.disconnect_called = False
#         self.keep_alive_task = asyncio.create_task(self.keep_alive())


# #Receive from websocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         if message == "pong":
#             return
#         else:
#             sender = self.scope["user"].username
#             chat_with_id = text_data_json["chat_with_id"]
#             await self.send_to_database(message, chat_with_id)
#             await self.channel_layer.group_send(self.chat_group_name, {"type": "chat.message", "message": message, "sender": sender})
            
#             await self.update_chat_viewed(self.chat_group_name, chat_with_id)


# #Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]
#         sender = event["sender"]
#         await self.send(text_data=json.dumps({"message": message, "sender": sender}))


#     @database_sync_to_async
#     def send_to_database(self, message, chat_with_id):
#         sender = self.scope["user"]
#         receiver = User.objects.get(id=chat_with_id)
#         if sender.id < receiver.id:
#             chat = Chat.objects.get(user1=sender.id, user2=receiver.id)
#         else:
#             chat = Chat.objects.get(user1=receiver.id, user2=sender.id)
#         message_obj = Message.objects.create(chat=chat, sender=sender, content=message)
#         message_obj.save()


#     async def disconnect(self, close_code):
#         #Leave chat group
#         if not self.disconnect_called:
#             self.disconnect_called = True
#             await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
#             await self.decrease_chat_group_count(self.chat_group_name)
#         if hasattr(self, "keep_alive_task"):
#             self.keep_alive_task.cancel()


#     async def keep_alive(self):
#         while True:
#             try:
#                 await self.send(text_data=json.dumps({"message": "ping"}))
#                 await asyncio.sleep(30)
#             except:
#                 await self.disconnect(1000)
#                 break


#     #If receiver in chat room at time of message received, will be used to update the associated ChatViewed instance
#     @database_sync_to_async
#     def increase_chat_group_count(self, chat_group_name):
#         obj, created = ChatGroupCurrentUserCount.objects.get_or_create(chat_group=chat_group_name)
#         if not created:
#             print('Adding 1 to CGCUC')
#             obj.connected_user_count += 1
#             obj.save()
#         print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
#         print(self.scope["user"].username)
#         print(obj.connected_user_count)


#     @database_sync_to_async
#     def decrease_chat_group_count(self, chat_group_name):
#         print('Minusing 1 from CGCUC')
#         ChatGroupCurrentUserCount.objects.filter(chat_group=chat_group_name).update(connected_user_count=F("connected_user_count") - 1)


#     @database_sync_to_async
#     def update_chat_viewed(self, chat_group_name, chat_with_id):
#         obj = ChatGroupCurrentUserCount.objects.get(chat_group=chat_group_name)
#         if obj.connected_user_count == 2:
#             User = get_user_model()
#             chat_with_user = get_object_or_404(User, pk=chat_with_id)
#             sender = self.scope["user"]
#             chat = Chat.objects.get(Q(user1=sender, user2=chat_with_user) | Q(user1=chat_with_user, user2=sender))
#             ChatViewed.objects.filter(user=chat_with_user, chat=chat).update()

#_____________________________________________________________________________________________________________________________
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_group_id = self.scope["url_route"]["kwargs"]["chat_group_id"]
        self.chat_group_name = f'chat_{self.chat_group_id}'

        #Add channel to channel group. self.channel_name is automatically generated when a Consumer instance is instiantiated
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.accept()

        await self.increase_chat_group_count(self.chat_group_name)

        self.disconnect_called = False
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
            await self.send_to_database(message, chat_with_id)
            await self.channel_layer.group_send(self.chat_group_name, {"type": "chat.message", "message": message, "sender": sender})
            
            await self.update_chat_viewed(self.chat_group_name, chat_with_id)


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
        if not self.disconnect_called:
            self.disconnect_called = True
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
            await self.decrease_chat_group_count(self.chat_group_name)
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


    #If receiver in chat room at time of message received, will be used to update the associated ChatViewed instance
    @database_sync_to_async
    def increase_chat_group_count(self, chat_group_name):
        obj, created = ChatGroupCurrentUserCount.objects.get_or_create(chat_group=chat_group_name)
        if not created:
            print('Adding 1 to CGCUC')
            obj.connected_user_count += 1
            obj.save()
        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        print(self.scope["user"].username)
        print(obj.connected_user_count)


    @database_sync_to_async
    def decrease_chat_group_count(self, chat_group_name):
        print('Minusing 1 from CGCUC')
        ChatGroupCurrentUserCount.objects.filter(chat_group=chat_group_name).update(connected_user_count=F("connected_user_count") - 1)


    @database_sync_to_async
    def update_chat_viewed(self, chat_group_name, chat_with_id):
        obj = ChatGroupCurrentUserCount.objects.get(chat_group=chat_group_name)
        if obj.connected_user_count == 2:
            User = get_user_model()
            chat_with_user = get_object_or_404(User, pk=chat_with_id)
            sender = self.scope["user"]
            chat = Chat.objects.get(Q(user1=sender, user2=chat_with_user) | Q(user1=chat_with_user, user2=sender))
            ChatViewed.objects.filter(user=chat_with_user, chat=chat).update()


# chat/consumers.py
from ast import keyword
import json
from urllib import request
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bot.models import Question

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connect")
        self.room_name = 'chatbot'
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnect")
        # Leave room group
        await(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("receive")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if self.scope['user'].username:
            # await self.save_question(message)
            await self.answer_question(message)
        else:
            pass
        # Send message to room group
        await(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        print("chat_message")
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_question(self, message):
        question = Question.objects.create(user_question=message)
        question.save()
        return 0
    

    async def answer_question(self, message):
        exclude_words = ['when', 'what', 'where', 'why', 'how', 'if']
        kwords = [i.lower() for i in message.split() if i.lower() not in exclude_words]
        question = Question.objects.filter(keyword__contains=message)
        event = {'message': '<html>\n hii</html>'}
        text_data_json = json.loads(json.dumps(event))
        message = text_data_json['message']

        # Send message to room group
        await(self.channel_layer.group_send)( self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
        return 0

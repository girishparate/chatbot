# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import re
from bot.models import Answer, Question

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chatbot'
        self.user = self.scope["user"]
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        await(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "Hello, "+str(self.user)
            }
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        if self.scope['user'].username:
            # await self.save_question(message)
            await self.answer_question(message)
        else:
            pass
        
    # Receive message from room group
    async def chat_message(self, event):
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
    
    @database_sync_to_async
    def answer_question(self, message):
        
        exclude_words = ['when', 'what', 'where', 'why', 'how', 'if', 'is']
        kwords = [i.lower() for i in message.split() if i.lower() not in exclude_words]
        strn = '<div>'
        for i in kwords:
            datas = re.sub(r'[^\w]', '', i)
            questiond = Question.objects.filter(keyword__contains=datas)
            for ique in questiond:
                data_anw = Answer.objects.filter(question=ique).values('answer', 'id')
                for anse in data_anw:
                    strn += '<div id='+str(anse['id'])+'>'+str(anse['answer'])+'</div><br>'
        
        strn += '</div>'
        event = {'message': strn}
        text_data_json = json.loads(json.dumps(event))
        message = text_data_json['message']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
        return 0

# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import re
from bot.models import Answer, Question
# import pandas as pd
# import numpy as np
import string
# import seaborn as sns
# import matplotlib.pyplot as plt
from nltk.corpus import stopwords
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfTransformer
# from sklearn.model_selection import train_test_split
# from sklearn.svm import SVC
# from collections import Counter
# from sklearn.metrics import classification_report,confusion_matrix
# from sklearn.model_selection import GridSearchCV


def transform_message(message):
    message_not_punc = [] # Message without punctuation
    i = 0
    for punctuation in message:
        if punctuation not in string.punctuation:
            message_not_punc.append(punctuation)
    # Join words again to form the string.
    message_not_punc = ''.join(message_not_punc) 

    # Remove any stopwords for message_not_punc, but first we should     
    # to transform this into the list.
    message_clean = list(message_not_punc.split(" "))
    while i <= len(message_clean):
        for mess in message_clean:
            if mess.lower()  in stopwords.words('english'):
                message_clean.remove(mess)
        i =i +1
    return  message_clean

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
        a=transform_message(message)
        
        kwords = [i.lower() for i in a.message_clean.split()]
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

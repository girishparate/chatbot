from django.shortcuts import render

# Create your views here.
# chat/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'chatbot.html')

def bot(request, room_name):
    return render(request, 'bot.html', {
        'room_name': room_name
    })
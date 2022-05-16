from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('bot/<str:room_name>', views.bot, name='home')
]
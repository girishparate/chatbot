from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bot/faq/(?P<room_name>\w+)/$', consumers.ChatFaqConsumer.as_asgi()),

    re_path(r'ws/bot/custom/(?P<room_name>\w+)/$', consumers.ChatCustomConsumer.as_asgi()),
]
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from dashboard import consumers

websocket_urlpatterns = [
    re_path('ws/sensor/', consumers.SensorConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),
})

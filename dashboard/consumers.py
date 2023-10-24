import json
from channels.generic.websocket import AsyncWebsocketConsumer
from dashboard.methonds import generate_live_heap_map


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("sensor", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("heatmap", self.channel_name)

    async def send_sensor_data(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def receive(self, text_data):
        data = json.loads(text_data)
        sensor = data['sensor']
        response_message = await generate_live_heap_map(sensor)
        await self.send(json.dumps({'type': 'map_updated', 'message': response_message}))

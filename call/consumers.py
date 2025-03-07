from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VideoChatConsumer(AsyncWebsocketConsumer):
    active_clients = {}

    async def connect(self):
        self.room_key = self.scope['url_route']['kwargs']['room_key']
        self.room_group_name = f'video_{self.room_key}'
        self.client_id = str(json.dumps(self.scope['client']))

        if self.room_group_name not in self.active_clients:
            self.active_clients[self.room_group_name] = set()
        self.active_clients[self.room_group_name].add(self.client_id)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Client {self.client_id} connected to room: {self.room_key}. Active clients: {self.active_clients[self.room_group_name]}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_update',
                'client_id': self.client_id,
                'action': 'connect'
            }
        )

    async def disconnect(self, close_code):
        if self.room_group_name in self.active_clients:
            self.active_clients[self.room_group_name].discard(self.client_id)
            print(f"Client {self.client_id} disconnected from room: {self.room_key}. Active clients: {self.active_clients[self.room_group_name]}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'client_update',
                    'client_id': self.client_id,
                    'action': 'disconnect'
                }
            )
            if not self.active_clients[self.room_group_name]:
                del self.active_clients[self.room_group_name]

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            if data.get('type') == 'ready':
                print(f"Client {self.client_id} is ready in room {self.room_key}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'client_ready',
                        'client_id': self.client_id
                    }
                )
        elif bytes_data:
            print(f"Received video chunk from {self.client_id} in room {self.room_key}, size: {len(bytes_data)}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_message',
                    'bytes_data': bytes_data,
                    'sender_id': self.client_id
                }
            )

    async def video_message(self, event):
        sender_id = event['sender_id']
        if sender_id != self.client_id:
            print(f"Relaying video chunk to {self.client_id} in room {self.room_key}, size: {len(event['bytes_data'])}")
            await self.send(bytes_data=event['bytes_data'])
        else:
            print(f"Skipping self-relay for {self.client_id}")

    async def client_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'client_update',
            'client_id': event['client_id'],
            'action': event['action']
        }))

    async def client_ready(self, event):
        await self.send(text_data=json.dumps({
            'type': 'client_ready',
            'client_id': event['client_id']
        }))
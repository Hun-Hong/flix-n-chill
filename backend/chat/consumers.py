import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # 방 그룹에 참가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # 연결시 이전 메시지 전송
        await self.send_previous_messages()

    async def disconnect(self, close_code):
        # 방 그룹에서 나가기
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # 메시지를 데이터베이스에 저장
        await self.save_message(username, message)

        # 방 그룹에 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': str(timezone.now())
            }
        )

    async def chat_message(self, event):
        # WebSocket으로 메시지 전송
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, username, message):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(id=self.room_id)
        Message.objects.create(
            room=room,
            sender=user,
            content=message
        )

    @database_sync_to_async
    def get_previous_messages(self):
        room = ChatRoom.objects.get(id=self.room_id)
        messages = room.messages.all().order_by('-timestamp')[:50]
        return [
            {
                'message': msg.content,
                'username': msg.sender.username,
                'timestamp': str(msg.timestamp)
            }
            for msg in reversed(messages)
        ]

    async def send_previous_messages(self):
        messages = await self.get_previous_messages()
        for message in messages:
            await self.send(text_data=json.dumps(message))

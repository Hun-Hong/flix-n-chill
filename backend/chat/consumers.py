# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL에서 room_id 추출
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # 인증된 사용자만 연결 허용
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # 채팅방 권한 확인
        if not await self.has_room_permission():
            await self.close()
            return
        
        # 그룹에 조인
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 기존 메시지 로드해서 전송
        messages = await self.get_room_messages()
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            message_content = data['message']
            
            # 메시지 저장
            message = await self.save_message(message_content)
            
            # 그룹의 모든 멤버에게 메시지 전송
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'sender': {
                            'id': message.sender.id,
                            'nickname': message.sender.nickname,
                            'profile_image': message.sender.profile_image.url if message.sender.profile_image else None
                        },
                        'timestamp': message.timestamp.isoformat(),
                        'is_read': message.is_read
                    }
                }
            )

    async def chat_message(self, event):
        # 그룹에서 받은 메시지를 WebSocket으로 전송
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    @database_sync_to_async
    def has_room_permission(self):
        """사용자가 해당 채팅방에 접근 권한이 있는지 확인"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return self.user in [room.participant1, room.participant2]
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """메시지를 데이터베이스에 저장"""
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        # 채팅방의 updated_at 갱신
        room.save()
        return message

    @database_sync_to_async
    def get_room_messages(self):
        """채팅방의 기존 메시지들을 가져오기"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            messages = room.messages.select_related('sender').order_by('timestamp')
            
            return [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'sender': {
                        'id': msg.sender.id,
                        'nickname': msg.sender.nickname,
                        'profile_image': msg.sender.profile_image.url if msg.sender.profile_image else None
                    },
                    'timestamp': msg.timestamp.isoformat(),
                    'is_read': msg.is_read
                }
                for msg in messages
            ]
        except ChatRoom.DoesNotExist:
            return []
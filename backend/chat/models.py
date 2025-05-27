# chat/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ChatRoom(models.Model):
    """1:1 채팅방"""
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_p2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['participant1', 'participant2']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat: {self.participant1.nickname} & {self.participant2.nickname}"
    
    @classmethod
    def get_or_create_room(cls, user1, user2):
        """두 사용자 간의 채팅방 가져오기 또는 생성"""
        # 사용자 순서를 정렬해서 중복 방지
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        room, created = cls.objects.get_or_create(
            participant1=user1,
            participant2=user2
        )
        return room, created

class Message(models.Model):
    """채팅 메시지"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.nickname}: {self.content[:50]}"
# chat/models.py
from django.db import models
from django.conf import settings  # 🔥 이것 추가!

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    # 🔥 수정: User 대신 settings.AUTH_USER_MODEL 사용
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    # 🔥 수정: User 대신 settings.AUTH_USER_MODEL 사용
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f'{self.sender.username}: {self.content[:50]}'
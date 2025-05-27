# chat/serializers.py
from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model  # 🔥 수정된 import

# 🔥 올바른 User 모델 가져오기
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class MessageSerializer(serializers.ModelSerializer):
    """메시지 시리얼라이저"""
    sender = UserSerializer(read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'sender', 'sender_name']
        read_only_fields = ['timestamp', 'sender']

class ChatRoomSerializer(serializers.ModelSerializer):
    """채팅방 조회용 시리얼라이저"""
    participants = UserSerializer(many=True, read_only=True)
    participant_count = serializers.IntegerField(source='participants.count', read_only=True)
    latest_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'created_at', 'participants', 
            'participant_count', 'latest_message', 'messages'
        ]
    
    def get_latest_message(self, obj):
        """최신 메시지 가져오기"""
        latest = obj.messages.last()
        if latest:
            return {
                'content': latest.content,
                'sender': latest.sender.username,
                'timestamp': latest.timestamp
            }
        return None

class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """채팅방 생성용 시리얼라이저"""
    participants = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="참가자 ID 목록 (선택사항)"
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'participants']
    
    def create(self, validated_data):
        participants_ids = validated_data.pop('participants', [])
        chat_room = ChatRoom.objects.create(**validated_data)
        
        # 채팅방 생성자도 참가자에 추가
        chat_room.participants.add(self.context['request'].user)
        
        # 추가 참가자들 추가
        if participants_ids:
            chat_room.participants.add(*participants_ids)
        
        return chat_room

class ChatRoomListSerializer(serializers.ModelSerializer):
    """채팅방 목록용 간단한 시리얼라이저"""
    participant_count = serializers.IntegerField(source='participants.count', read_only=True)
    latest_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_at', 'participant_count', 'latest_message']
    
    def get_latest_message(self, obj):
        """최신 메시지 요약"""
        latest = obj.messages.last()
        if latest:
            return {
                'content': latest.content[:50] + ('...' if len(latest.content) > 50 else ''),
                'sender': latest.sender.username,
                'timestamp': latest.timestamp
            }
        return None

class MessageCreateSerializer(serializers.ModelSerializer):
    """메시지 생성용 시리얼라이저 (REST API용)"""
    class Meta:
        model = Message
        fields = ['content']
    
    def create(self, validated_data):
        # sender와 room은 view에서 설정
        return Message.objects.create(**validated_data)
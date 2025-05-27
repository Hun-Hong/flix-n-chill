from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.ChatRoomListView.as_view(), name='chat-rooms'),
    path('rooms/<int:room_id>/', views.ChatRoomDetailView.as_view(), name='chat-room-detail'),
]

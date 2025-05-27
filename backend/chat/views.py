from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ChatRoom
from .authentication import token_required

# views.py 수정
@token_required
def chat_with(request, user_id):
    other = get_object_or_404(get_user_model(), pk=user_id)
    room, created = ChatRoom.get_or_create_room(request.user, other)  

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "room_id": room.id,
            "partner": {
                "id": other.id,
                "username": other.username,
                "nickname": other.nickname if hasattr(other, 'nickname') else other.username,
                "profile_image": other.profile_image.url if hasattr(other, 'profile_image') and other.profile_image else None
            },
            "created_at": room.created_at.isoformat(),
            "updated_at": room.updated_at.isoformat()
        })
    return redirect("chat:room", room_id=room.id)

@token_required
def latest_room(request):
    room = (
        ChatRoom.objects
        .filter(Q(participant1=request.user) | Q(participant2=request.user))  
        .order_by("-updated_at")
        .select_related("participant1", "participant2") 
        .first()
    )
    if not room:
        return JsonResponse({}, status=204)

    partner = room.participant2 if room.participant1 == request.user else room.participant1  
    return JsonResponse({
        "room_id": room.id,
        "partner": {
            "id": partner.id,
            "username": partner.username,
            "nickname": partner.nickname if hasattr(partner, 'nickname') else partner.username,
            "profile_image": partner.profile_image.url if hasattr(partner, 'profile_image') and partner.profile_image else None
        },
        "created_at": room.created_at.isoformat(),
        "updated_at": room.updated_at.isoformat()
    })

@token_required
def chat_room(request, room_id):
    # 채팅방 조회
    room = get_object_or_404(ChatRoom, id=room_id)

    # 접근 권한 확인
    if request.user not in [room.participant1, room.participant2]:
        return JsonResponse(
            {"error": "You don't have permission to access this chat room"},
            status=403
        )

    # 상대방 정보
    partner = room.participant2 if room.participant1 == request.user else room.participant1

    # JSON 응답 반환
    return JsonResponse({
        "room_id": room.id,
        "partner": {
            "id": partner.id,
            "username": partner.username,
            "nickname": getattr(partner, 'nickname', partner.username),
            "profile_image": partner.profile_image.url if getattr(partner, 'profile_image', None) else None
        },
        "created_at": room.created_at.isoformat(),
        "updated_at": room.updated_at.isoformat()
    })

@token_required
def current_user(request):
    user = request.user
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "nickname": getattr(user, 'nickname', user.username),
        "profile_image": user.profile_image.url if getattr(user, 'profile_image', None) else None,
    })
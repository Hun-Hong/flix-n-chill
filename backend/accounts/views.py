from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from dj_rest_auth.views import UserDetailsView
from .serializers import UserProfileSerializer, UserUpdateSerializer
from accounts.models import Follow


# Create your views here.
User = get_user_model()

class EmailDuplicateCheckView(APIView):
    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response({"error": "email is required"}, status=status.HTTP_400_BAD_REQUEST)

        is_duplicate = User.objects.filter(email=email).exists()
        return Response({"is_duplicate": is_duplicate})


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def follow(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)

    if user == request.user:
        return Response({'error': "자기 자신은 팔로우할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "POST":
        if Follow.objects.filter(follower=request.user, following=user).exists():
            return Response({'error': "이미 팔로우 중입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        Follow.objects.create(follower=request.user, following=user)
        
        # 팔로우 성공 후 업데이트된 팔로워/팔로잉 수 반환
        return Response({
            'detail': "팔로우 성공!",
            'is_following': True,
            'followers_count': user.followers.count(),
            'following_count': request.user.following.count()
        }, status=status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        # 수정: exists() 확인을 올바르게 수정
        follow_relation = Follow.objects.filter(follower=request.user, following=user)
        if not follow_relation.exists():
            return Response({'error': "팔로우한 적이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        follow_relation.delete()
        
        # 언팔로우 성공 후 업데이트된 팔로워/팔로잉 수 반환
        return Response({
            'detail': "언팔로우 성공!",
            'is_following': False,
            'followers_count': user.followers.count(),
            'following_count': request.user.following.count()
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_follow_status(request, user_pk):
    """특정 사용자와의 팔로우 상태 확인"""
    user = get_object_or_404(User, pk=user_pk)
    
    if user == request.user:
        return Response({'error': "자기 자신과의 팔로우 상태는 확인할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    return Response({
        'is_following': is_following,
        'followers_count': user.followers.count(),
        'following_count': user.following.count()
    }, status=status.HTTP_200_OK)


class CustomUserDetailsView(UserDetailsView):
    serializer_class = UserProfileSerializer

@api_view(["GET", "PUT"])
def detail(request, user_pk):
    if request.method == "GET":
        user = get_object_or_404(User, pk=user_pk)
        
        # 디버깅 정보 출력
        print(f"Request user: {request.user}")
        print(f"Request user authenticated: {request.user.is_authenticated}")
        print(f"Target user: {user}")
        print(f"Target user's liked movies: {user.like_movie.all()}")
        
        # 특정 영화로 테스트
        if user.like_movie.exists():
            first_movie = user.like_movie.first()
            print(f"First liked movie: {first_movie}")
            print(f"Movie's liked_user field: {first_movie.liked_user.all()}")
            print(f"Is request.user in liked_user? {first_movie.liked_user.filter(id=request.user.id).exists()}")
        
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)


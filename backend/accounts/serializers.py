from rest_framework import serializers
from .models import User
from movies.models import Movie, Review, Genre
from accounts.models import Follow, MovieLike
# from movies.serializers import MovieListSerializer  # 이 import 제거
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import models

# 독립적인 MovieListSerializer 정의
class MovieListSerializer(serializers.ModelSerializer):
    class GenreSerializer(serializers.ModelSerializer):
        class Meta:
            model = Genre
            fields = "__all__"

    average_rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = ("id", "vote_average", "poster_path", "release_date", "genres", "title", "original_title", "is_liked", "average_rating")
        read_only_fields = ("genres", "is_liked")  # 오타 수정: read_only_field → read_only_fields

    def get_is_liked(self, obj):
        request = self.context.get("request", None)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return obj.liked_user.filter(id=user.id).exists()
        return False
    
    def get_average_rating(self, obj):
        reviews = obj.review_set.all()
        if reviews.exists():
            return round(reviews.aggregate(avg=models.Avg('rating'))['avg'], 2)
        return None


class ReviewSimpleSerializer(serializers.ModelSerializer):
    # 리뷰에 필요한 영화 정보는 간단하게
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_id = serializers.IntegerField(source='movie.id', read_only=True)
    poster_path = serializers.CharField(source='movie.poster_path', read_only=True)
    class Meta:
        model = Review
        fields = '__all__'  # 또는 필요한 필드들만 명시


class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(required=True, max_length=20)
    birth = serializers.DateField(required=True)
    gender = serializers.BooleanField(required=True)
    profile_image = serializers.ImageField(required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname')
        data['birth'] = self.validated_data.get('birth')
        data['gender'] = self.validated_data.get('gender')
        data['profile_image'] = self.validated_data.get('profile_image')
        print(data)
        return data
    
    def save(self, request):
        user = super().save(request)
        user.nickname = self.validated_data.get('nickname')
        user.birth = self.validated_data.get('birth')
        user.gender = self.validated_data.get('gender')
        user.profile_image = self.validated_data.get('profile_image')  # 오타 수정: profile_imgae → profile_image
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    like_movies = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()  # 추가
    activities = serializers.SerializerMethodField()  # 이것만 추가


    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile_image', "last_login",
            'followers_count', 'following_count', 'followers', 'following',
            'reviews', 'like_movies', 'nickname', "birth", "profile_bio", "gender", "is_following", "activities"
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers(self, obj):
        followers_data = []
        for follower in obj.followers.all():
            followers_data.append({
                'id': follower.id,
                'username': follower.username,
                'nickname': follower.nickname,
                'profile_image': follower.profile_image.url if follower.profile_image else None,
                'profile_bio': follower.profile_bio,
                'followers_count': follower.followers.count(),
                'following_count': follower.following.count(),
                'is_following': self._check_is_following(follower)
            })
        return followers_data

    def get_following(self, obj):
        following_data = []
        for following in obj.following.all():
            following_data.append({
                'id': following.id,
                'username': following.username,
                'nickname': following.nickname,
                'profile_image': following.profile_image.url if following.profile_image else None,
                'profile_bio': following.profile_bio,
                'followers_count': following.followers.count(),
                'following_count': following.following.count(),
                'is_following': self._check_is_following(following)
            })
        return following_data

    def _check_is_following(self, target_user):
        """팔로우 상태 확인 헬퍼 메서드"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if request.user == target_user:
            return False
        return Follow.objects.filter(follower=request.user, following=target_user).exists()

    def get_reviews(self, obj):
        reviews = Review.objects.filter(user=obj).select_related('movie')
        return ReviewSimpleSerializer(reviews, many=True, context=self.context).data
    
    def get_like_movies(self, obj):
        # 프로필 소유자를 context에 추가하여 전달
        context_with_owner = self.context.copy()
        context_with_owner['profile_owner'] = obj
        
        # prefetch_related로 성능 최적화
        liked_movies = obj.like_movie.all().prefetch_related('genres', 'review_set')
        serializer = ProfileMovieSerializer(liked_movies, many=True, context=context_with_owner)
        return serializer.data

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        if request.user == obj:
            return False  # 자기 자신은 팔로우할 수 없음
        
        return Follow.objects.filter(follower=request.user, following=obj).exists()

    def get_activities(self, obj):
    # 활동 제한 개수 (기본 30개)
        limit = 30
        activities = []
        
        try:
            # 1. 리뷰 작성 내역
            reviews = Review.objects.filter(user=obj).select_related('movie')[:limit]
            for review in reviews:
                activities.append({
                    'id': f"review_{review.id}",
                    'type': 'review',
                    'action': 'created',
                    'text': f'"{review.movie.title}"에 리뷰를 작성했습니다',
                    'detail': {
                        'movie_id': review.movie.id,
                        'movie_title': review.movie.title,
                        'movie_poster': review.movie.poster_path,
                        'rating': review.rating,
                        'content': review.comment[:100] + '...' if len(review.comment or '') > 100 else review.comment
                    },
                    'created_at': review.created_at,
                    'timestamp': review.created_at.isoformat()
                })
            
            # 2. 팔로우 내역
            follows = Follow.objects.filter(follower=obj).select_related('following')[:limit]
            for follow in follows:
                activities.append({
                    'id': f"follow_{follow.id}",
                    'type': 'follow',
                    'action': 'followed',
                    'text': f'{follow.following.nickname}님을 팔로우했습니다',
                    'detail': {
                        'user_id': follow.following.id,
                        'user_nickname': follow.following.nickname,
                        'user_profile_image': follow.following.profile_image.url if follow.following.profile_image else None
                    },
                    'created_at': follow.created_at,
                    'timestamp': follow.created_at.isoformat()
                })
            
            # 3. 영화 좋아요 내역
            movie_likes = MovieLike.objects.filter(user=obj).select_related('movie')[:limit]
            for like in movie_likes:
                activities.append({
                    'id': f"like_{like.id}",
                    'type': 'like',
                    'action': 'liked',
                    'text': f'"{like.movie.title}"을 좋아요했습니다',
                    'detail': {
                        'movie_id': like.movie.id,
                        'movie_title': like.movie.title,
                        'movie_poster': like.movie.poster_path,
                        'movie_rating': like.movie.vote_average
                    },
                    'created_at': like.created_at,
                    'timestamp': like.created_at.isoformat()
                })
            
            # 모든 활동을 시간순으로 정렬 (최신순)
            activities.sort(key=lambda x: x['created_at'], reverse=True)
            
            # 제한된 개수만 반환
            return activities[:limit]
            
        except Exception as e:
            print(f"활동 로그 생성 중 오류: {e}")
            return []



class ProfileMovieSerializer(serializers.ModelSerializer):
    class GenreSerializer(serializers.ModelSerializer):
        class Meta:
            model = Genre
            fields = "__all__"

    average_rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = ("id", "vote_average", "poster_path", "release_date", "genres", "title", "original_title", "is_liked", "average_rating")
        read_only_fields = ("genres", "is_liked")

    def get_is_liked(self, obj):
        # context에서 프로필 소유자 정보 가져오기
        profile_owner = self.context.get('profile_owner')
        if profile_owner:
            return obj.liked_user.filter(id=profile_owner.id).exists()
        return False
    
    def get_average_rating(self, obj):
        reviews = obj.review_set.all()
        if reviews.exists():
            return round(reviews.aggregate(avg=models.Avg('rating'))['avg'], 2)
        return None

class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('nickname', 'profile_bio', 'profile_image')
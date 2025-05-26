from rest_framework import serializers
from .models import User
from movies.models import Movie, Review, Genre
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

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile_image', "last_login",
            'followers_count', 'following_count', 'followers', 'following',
            'reviews', 'like_movies', 'nickname', "birth", "profile_bio", "gender"
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers(self, obj):
        return obj.followers.values('id', 'username')

    def get_following(self, obj):
        return obj.following.values('id', 'username')

    def get_reviews(self, obj):
        reviews = Review.objects.filter(user=obj).select_related('movie')
        return ReviewSimpleSerializer(reviews, many=True, context=self.context).data
    
    def get_like_movies(self, obj):
        liked_movies = obj.like_movie.all()
        
        # 프로필 소유자를 context에 추가하여 전달
        context_with_owner = self.context.copy()
        context_with_owner['profile_owner'] = obj  # 프로필 소유자 정보 추가
        
        serializer = ProfileMovieSerializer(liked_movies, many=True, context=context_with_owner)
        return serializer.data

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
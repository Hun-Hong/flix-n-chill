from rest_framework import serializers
from .models import User, Review
from movies.models import Movie

class ReviewSimpleSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title')

    class Meta:
        model = "movies.review"
        fields = "__all__"

class MovieSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_path']

class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    like_movies = MovieSimpleSerializer(source="like_movie", many=True)
    profile_image = serializers.ImageField(source="profile_image", required=False)  # 프로필 이미지 필드명 맞게 변경

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile_image',
            'followers_count', 'following_count', 'followers', 'following',
            'reviews', 'like_movies'
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
        return ReviewSimpleSerializer(reviews, many=True).data

from rest_framework import serializers
from .models import Movie, MovieProvider, Genre, Review, Comment
from django.db import models
from accounts.models import User

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
        read_only_fields = ("genres", "is_liked")

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



class MovieCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"
        read_only_fields = ("rating", "genres")


class MovieDetailSerializer(serializers.ModelSerializer):
    class ProviderSerializer(serializers.ModelSerializer):
        class Meta:
            model = MovieProvider
            fields = "__all__"

    isLiked = serializers.SerializerMethodField()
    isReviewed = serializers.SerializerMethodField()
    providers = ProviderSerializer(many=True)

    class Meta:
        model = Movie
        fields = "__all__"
        read_only_fields = ("rating", "genres")

    def get_isLiked(self, obj):
        request = self.context.get("request", None)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return obj.liked_user.filter(id=user.id).exists()
        return False

    def get_isReviewed(self, obj):
        request = self.context.get("request", None)
        user    = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return Review.objects.filter(movie=obj, user=user).exists()
        return False


class ReviewSerializer(serializers.ModelSerializer):
    class movieSerializer(serializers.ModelSerializer):
        class Meta:
            model = Movie
            fields = ("id", "title", "poster_path", )

    movie = movieSerializer()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("user", "movie", "created_at")

    def get_comments(self, obj):
        comments = obj.comments.filter(parent_comment=None).order_by('created_at')
        return CommentSerializer(comments, many=True, context=self.context).data


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("user", "movie", "created_at")


class CommentUserSerializer(serializers.ModelSerializer):
    """Serializer for user information in comments"""
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'profile_image')


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for displaying comments"""
    user = CommentUserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'review', 'parent_comment', 'content', 'created_at', 'like_count', 'is_liked', 'replies')
        read_only_fields = ('user', 'review', 'parent_comment', 'created_at')

    def get_is_liked(self, obj):
        request = self.context.get("request", None)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False

    def get_replies(self, obj):
        # Only get direct replies to this comment
        replies = obj.replies.all().order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    class Meta:
        model = Comment
        fields = ('id', 'review', 'parent_comment', 'content', 'created_at')
        read_only_fields = ('created_at',)

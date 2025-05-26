from rest_framework import serializers
from .models import Movie, MovieProvider, Genre, Review
from django.db import models

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
        read_only_field = ("genres", "is_liked")

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
        read_only_field = ("rating", "genres")


class MovieDetailSerializer(serializers.ModelSerializer):
    class ProviderSerializer(serializers.ModelSerializer):
        class Meta:
            model = MovieProvider
            fields = "__all__"

    providers = ProviderSerializer(many=True)

    class Meta:
        model = Movie
        fields = "__all__"
        read_only_field = ("rating", "genres")


class ReviewSerializer(serializers.ModelSerializer):
    class movieSerializer(serializers.ModelSerializer):
        class Meta:
            model = Movie
            fields = ("id", "title", "poster_path", )

    movie = movieSerializer()

    class Meta:
        model = Review
        field = "__all__"
        read_only_field = ("user", "movie", "created_at")

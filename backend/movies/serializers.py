from rest_framework import serializers
from .models import Movie, MovieProvider, Genre


class MovieListSerializer(serializers.ModelSerializer):
    class GenreSerializer(serializers.ModelSerializer):
        class Meta:
            model = Genre
            fields = "__all__"

    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = ("id", "vote_average", "poster_path", "release_date", "genres", "title", "original_title")
        read_only_field = ("genres")


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


class ProviderSerilizer(serializers.ModelSerializer):
    class Meta:
        model = MovieProvider
        fields = "__all__"
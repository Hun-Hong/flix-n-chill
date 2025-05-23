from rest_framework import serializers
from .models import Movie, MovieProvider

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"
        read_only_field = ("rating", "genres")

class ProviderSerilizer(serializers.ModelSerializer):
    class Meta:
        model = MovieProvider
        fields = "__all__"
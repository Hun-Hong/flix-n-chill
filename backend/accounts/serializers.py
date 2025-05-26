from rest_framework import serializers
from .models import User
from movies.models import Movie, Review
from dj_rest_auth.registration.serializers import RegisterSerializer

class ReviewSimpleSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title')

    class Meta:
        model = "movies.review"
        fields = "__all__"

class MovieSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_path']


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
        user.profile_image = self.validated_data.get('profile_imgae')
        user.save()
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    like_movies = MovieSimpleSerializer(source="like_movie", many=True)

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
        return ReviewSimpleSerializer(reviews, many=True).data


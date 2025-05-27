from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(max_length=20)
    birth = models.DateField(default=datetime.datetime(2000, 1, 1))
    profile_bio = models.CharField(max_length=200, default="", blank=True)
    gender = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile/', blank=True, default='profile/default.png')

    following = models.ManyToManyField(
        "self", 
        through='Follow',
        related_name="followers", 
        symmetrical=False,
        blank=True
    )
    
    like_movie = models.ManyToManyField(
        "movies.Movie", 
        through='MovieLike',
        related_name="liked_user",
        blank=True
    )
    
    def __str__(self):
        return self.nickname or self.username
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'


class Follow(models.Model):
    follower = models.ForeignKey('User', related_name='following_relations', on_delete=models.CASCADE)
    following = models.ForeignKey('User', related_name='follower_relations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        verbose_name = '팔로우'
        verbose_name_plural = '팔로우 목록'
    
    def __str__(self):
        return f"{self.follower.nickname} → {self.following.nickname}"


class MovieLike(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
        verbose_name = '영화 좋아요'
        verbose_name_plural = '영화 좋아요 목록'
    
    def __str__(self):
        return f"{self.user.nickname} likes {self.movie.title}"


class ReviewLike(models.Model):
    """리뷰 좋아요 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_likes'
    )
    review = models.ForeignKey(
        'movies.Review',  # movies 앱의 Review 모델
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')  # 중복 좋아요 방지
        db_table = 'accounts_reviewlike'

    def __str__(self):
        return f'{self.user.username} likes {self.review.id}'

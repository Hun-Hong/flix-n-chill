from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(max_length=20)
    birth = models.DateField(default=datetime.datetime(2000,1,1))
    profile_bio = models.CharField(max_length=30, default="")
    gender = models.BooleanField(default=False)
    following = models.ManyToManyField("accounts.user", related_name="followers", symmetrical=False)
    like_movie = models.ManyToManyField("movies.movie", related_name="liked_user")
    profile_image = models.ImageField(upload_to='profile/', blank=True, default='profile/default.png')
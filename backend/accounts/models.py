from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    following = models.ManyToManyField("accounts.user", related_name="followers", symmetrical=False)
    like_movie = models.ManyToManyField("movies.movie", related_name="liked_user")
    profile_image = models.ImageField(upload_to='profile/', blank=True, default='profile/default.png')
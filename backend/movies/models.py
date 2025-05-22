from django.db import models

# Create your models here.
class Movie(models.Model):
    rating = models.ManyToManyField("accounts.user", through='movies.review')

    title = models.CharField(max_length=100)
    original_title = models.CharField(max_length=100)
    
    overview = models.TextField(blank=True)
    
    adult = models.BooleanField()
    budget = models.PositiveIntegerField()
    genres = models.ManyToManyField("movies.genre", blank=True)
    tmdb_id = models.PositiveIntegerField()
    origin_country = models.CharField(max_length=50)
    runtime = models.PositiveIntegerField()
    release_date = models.DateField()
    tagline = models.CharField(max_length=100, blank=True)
    vote_average = models.FloatField()
    poster_path = models.CharField(max_length=100)

class Review(models.Model):
    user = models.ForeignKey("accounts.user", on_delete=models.CASCADE)
    movie = models.ForeignKey("movies.movie", on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Genre(models.Model):
    name = models.CharField(max_length=50)
    tmdb_id = models.PositiveIntegerField()

class OTTAvailability(models.Model):
    platform_name = models.CharField(max_length=50)

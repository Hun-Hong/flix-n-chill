from django.db import models

# Create your models here.
class Movie(models.Model):
    rating = models.ManyToManyField("accounts.user", through='movies.review')

    title = models.CharField(max_length=100)
    original_title = models.CharField(max_length=100)

    overview = models.TextField(blank=True)

    providers = models.ManyToManyField("movies.movieprovider", blank=True)

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
    comment = models.CharField(max_length=50, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    unique_together = ('user', 'movie')

class Comment(models.Model):
    user = models.ForeignKey("accounts.user", on_delete=models.CASCADE)
    review = models.ForeignKey("movies.review", on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("accounts.user", related_name="liked_comments", blank=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"

    @property
    def like_count(self):
        return self.likes.count()

class Genre(models.Model):
    name = models.CharField(max_length=50)
    tmdb_id = models.PositiveIntegerField()

class MovieProvider(models.Model):
    name = models.CharField(max_length=50)
    tmdb_id = models.PositiveIntegerField()
    logo_path = models.CharField(max_length=100)

from django.db import models
from django.contrib.auth.models import User

class Trailer(models.Model):
    ranking = models.IntegerField()
    title = models.CharField(max_length=100)
    synopsis = models.TextField()
    trailer_url = models.URLField()
    release_date = models.DateField()
    total_views_last_7_days = models.IntegerField()

class Film(models.Model):
    title = models.CharField(max_length=100)
    synopsis = models.TextField()
    trailer_url = models.URLField()
    release_date = models.DateField()

class Series(models.Model):
    title = models.CharField(max_length=100)
    synopsis = models.TextField()
    trailer_url = models.URLField()
    release_date = models.DateField()

class Episode(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    synopsis = models.TextField()
    duration = models.DurationField()
    release_date = models.DateField()
    video_url = models.URLField()
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='episodes')

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    content = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    trailer = models.ForeignKey(Trailer, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

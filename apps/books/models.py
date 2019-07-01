from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=150, help_text='Book\'s title.')
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    db_table = 'Book'


class BookReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    review = models.TextField(blank=True, help_text='User\'s book review.')
    rating = models.IntegerField(help_text='User\'s book rate')

    class Meta:
        db_table = 'BookReview'


class Genre(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        db_table = 'Genre'

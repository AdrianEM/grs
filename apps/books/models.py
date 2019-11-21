from django.contrib.auth.models import User
from django.db import models
from languages.fields import LanguageField
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserProfile
from goodreads.settings import AUTHOR_ROLE, BOOK_FORMAT, MEDIA_TYPE, BOOK_PACE, BOOK_TONE, WRITING_STYLE, \
    NARRATION_PERSPECTIVE, BOOK_TIME


class Book(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, help_text=_('Book\'s title.'))
    sort_by_title = models.CharField(max_length=150, help_text=_('Sort by title'), db_column='sortByTitle')
    authors = models.ManyToManyField('Author', through='BookAuthor')
    orig_title = models.CharField(max_length=150, help_text=_('Original title'), null=True, db_column='origTitle')
    orig_pub_date = models.DateField(null=True, help_text=_('Original publication date'), db_column='origPubDate')
    media_type = models.CharField(choices=MEDIA_TYPE, max_length=2, default='B', db_column='mediaType')
    series = models.ForeignKey('BookSeries', on_delete=models.CASCADE)
    series_number = models.IntegerField(null=True, db_column='SeriesNumber')

    class Meta:
        db_table = 'Book'


class BookAuthor(models.Model):
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    primary_author = models.IntegerField(null=True, db_column='PrimaryAuthor', help_text=_('Primary author'))

    class Meta:
        db_table = 'BookAuthor'


class BookEdition(TimeStampedModel):
    isbn = models.BigIntegerField(help_text=_('ISBN'), null=True, unique=True)
    publisher = models.CharField(max_length=150, help_text=_('Publisher'), null=True)
    published = models.DateField(help_text=_('Published'), null=True)
    pages = models.IntegerField(help_text=_('Number of pages'), null=True)
    edition = models.CharField(max_length=150, help_text=_('Edition'), null=True)
    format = models.CharField(choices=BOOK_FORMAT, help_text=_('Format'), max_length=3, default='PB')
    description = models.TextField(help_text=_('Description'), null=True)
    language = LanguageField(default='en')
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    cover = models.ImageField(null=True)

    class Meta:
        db_table = 'BookEdition'


class BookReview(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='book_reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField(blank=True, help_text='User\'s book review.')
    rating = models.IntegerField(help_text='User\'s book rate')

    class Meta:
        db_table = 'BookReview'


class BookSeries(TimeStampedModel):
    name = models.CharField(max_length=150, help_text=_('Name'))

    class Meta:
        db_table = 'BookSeries'


class Genre(TimeStampedModel):
    name = models.CharField(max_length=150)

    class Meta:
        db_table = 'Genre'
        

class Author(TimeStampedModel):
    first_name = models.CharField(max_length=150, help_text=_('FirstName'), db_column='FirstName')
    last_name = models.CharField(max_length=150, help_text=_('Last Name'), db_column='LastName', null=True)
    role = models.CharField(max_length=2, help_text=_(''), choices=AUTHOR_ROLE, default='AU', null=True)

    class Meta:
        db_table = 'Author'


class BookMetadata(TimeStampedModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='metadata')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='book_metadata')
    is_fiction = models.BooleanField(default=True, help_text=_('Is this book fiction or nonfiction?'), null=True)
    genre = models.ForeignKey(Genre, related_name='books_metadata', on_delete=models.CASCADE, null=True)
    pace = models.CharField(choices=BOOK_PACE, help_text=_('What is the pace of this book?'), null=True, max_length=3)
    tone = models.CharField(choices=BOOK_TONE,
                            help_text=_('What is the tone of this book (bleak, romantic, upbeat, violent, etc.)'),
                            null=True, max_length=3)
    style = models.CharField(choices=WRITING_STYLE,
                             help_text=_('What is the writing style of this book (such as journalistic, descriptive,'
                                         ' scholarly, accessible, etc.)?'),
                             null=True, max_length=3)
    perspective = models.CharField(choices=NARRATION_PERSPECTIVE,
                                   help_text=_('What is the perspective of the narration?'), null=True, max_length=3)
    tense = models.CharField(choices=BOOK_TIME, help_text=_('Is this book told in the past, present, or future tense?'),
                             null=True, max_length=3)
    strong_female_character = models.BooleanField(null=True,
                                                  help_text=_('Do you think there is a strong '
                                                              'female character in this book?'))
    strong_male_character = models.BooleanField(null=True, help_text=_('Do you think there is a strong male character'
                                                                       ' in this book?'))
    few_characters = models.BooleanField(null=True, help_text=_('Does this book follow a few characters or many?'))

    class Meta:
        db_table = 'BookMetadata'


class Shelve(TimeStampedModel):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, help_text=_('Shelve\' owner.'),
                              related_name='shelves')
    name = models.CharField(max_length=150, help_text=_('Name'), db_column='Name')

    class Meta:
        db_table = 'Shelve'


class BookShelve(TimeStampedModel):
    shelve = models.ForeignKey(Shelve, on_delete=models.CASCADE, related_name='books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='shelves')

    class Meta:
        db_table = 'BookShelve'


class FavoriteGenre(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='users')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='genres')

    class Meta:
        db_table = 'FavoriteGenre'


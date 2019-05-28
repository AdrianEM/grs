from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django_countries.fields import CountryField
from model_utils.models import TimeStampedModel

from apps.books.models import Book
from goodreads.settings import GENDER, PERMISSION_VIEW, AGE_BIRTHDAY_PRIVACY


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    birthday = models.DateField(db_column='Birthday', help_text='User\'s birthday.')
    who_can_see_last_name = models.CharField(choices=PERMISSION_VIEW, max_length=2)
    photo = models.ImageField(help_text='User\'s profile image.', db_column='Photo', blank=True)
    city = models.CharField(max_length=70, help_text='User\'s city', blank=True, db_column='City')
    state = models.CharField(max_length=70, help_text='User\'s state/province.', db_column='State')
    country = CountryField(blank_label='Select yur country', help_text='User\'s country')
    location_view = models.CharField(choices=PERMISSION_VIEW, help_text='Who can see user\'s location.', max_length=2)
    gender = models.CharField(choices=GENDER, help_text='User\'s gender.', max_length=2)
    gender_view = models.CharField(choices=PERMISSION_VIEW, help_text='Who can see user\'s gender', max_length=2)
    age_view = models.CharField(choices=AGE_BIRTHDAY_PRIVACY, help_text='Who can see user\'s age and birthday.',
                                max_length=2)
    web_site = models.URLField(help_text='User\'s personal web site.', blank=True)
    interests = models.TextField(help_text='User\'s interests separated by coma.', blank=True)
    kind_books = models.TextField(help_text='User\'s book subject preferences.', blank=True)
    about_me = models.TextField(help_text='A short review about user.', blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'UserProfile'

    def __str__(self):
        return "{} {}".format(self.user.first_name,self.user.last_name)


class Shelve(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, help_text='Shelve\' owner.', related_name='shelves')
    name = models.CharField(max_length=150, help_text='Shelve\'s name.')

    class Meta:
        db_table = 'Shelve'


class BookShelve(models.Model):
    shelve = models.ForeignKey(Shelve, on_delete=models.CASCADE, related_name='books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='shelves')

    class Meta:
        db_table = 'BookShelve'


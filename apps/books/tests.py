import json
import tempfile

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile, EmailSettings, FeedSetting, ReadingGroup, ReadingGroupUsers
from apps.accounts.serializers import UserProfileSerializer, EmailSettingSerializer, FeedSettingSerializer

from django.utils.translation import gettext_lazy as _

from apps.books.models import Genre


class BaseViewTest(APITestCase):
    client = APIClient()
    token = {}

    @staticmethod
    def create_user_profile(username, email, password, first_name, last_name, birthday, who_can_see_last_name,
                            photo, city, state, country, location_view, gender, gender_view,
                            age_view, web_site="", interests="", kind_books="", about_me="", active=True):
        user = User(username=username, email=email, password=make_password(password), first_name=first_name,
                    last_name=last_name)
        user.save()
        user_profile = UserProfile(user=user, birthday=birthday, who_can_see_last_name=who_can_see_last_name,
                                   photo=photo, city=city, state=state, country=country, location_view=location_view,
                                   gender=gender, gender_view=gender_view, age_view=age_view, web_site=web_site,
                                   interests=interests, kind_books=kind_books, about_me=about_me, active=active)
        user_profile.save()

    @staticmethod
    def create_image():
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image = Image.new("RGB", (200, 200), "white")
            image.save(f, "PNG")

        return open(f.name, mode="rb")

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    def create_genre_for_book_tests():
        genre = Genre(name="Ficcion")
        genre.save()
        return genre

    def setUp(self):
        self.create_user_profile("meninleo", "meninleo@gmail.com", "meninleo", "Adrian", "Mena",
                                 "1990-08-15", "F", "", "Montevideo", "Montevideo", "NZ", "F", "M", "F",
                                 1)
        user = User.objects.get(pk=1)
        self.token = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION="Goodreads " + self.token["access"])


class BookTests(BaseViewTest):

    book_data = {
        "title": "La isla infinita",
        "genre": BaseViewTest.create_genre_for_book_tests().id,
        "sort_by_title": "isla infinita, La",
        "authors": [
            {
                "first_name": "Mario",
                "last_name": "Conde",
                "role": "AU"
            },
            {
                "first_name": "Leonardo",
                "last_name": "Padura",
                "role": "AU"
            },
            {
                "first_name": "Mario",
                "last_name": "Conde",
                "role": "AU"
            }
        ],
        "isbn": 1234567891234,
        "publisher": "Ernesto Daranas",
        "published": "2015-02-02",
        "pages": 458,
        "edition": "2019",
        "format": "PB",
        "description": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has "
                       "been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took "
                       "a galley of type and scrambled it to make a type specimen book. It ha",
        "edition_language": "es",
        "orig_title": "La isla Infinita",
        "orig_pub_date": "2015-01-03",
        "media_type": "B"
    }

    def test_create_book(self):
        payload = json.dumps(self.book_data)
        response = self.client.post(reverse("books-list"), data=payload, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.book_data['title'], response.data['title'])

    def test_create_book_fail(self):
        response = self.client.post(reverse("books-list"))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


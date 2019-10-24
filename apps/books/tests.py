import json
import tempfile

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile

from apps.books.models import Genre, Book


class BaseViewTest(APITestCase):
    client = APIClient()
    token = {}

    @staticmethod
    def create_user_profile(username, email, password, full_name, birthday, who_can_see_last_name,
                            photo, city, state, country, location_view, gender, gender_view,
                            age_view, web_site="", interests="", kind_books="", about_me="", active=True):

        user_profile = UserProfile(username=username, email=email, password=make_password(password),
                                   full_name=full_name, birthday=birthday,
                                   who_can_see_last_name=who_can_see_last_name, photo=photo, city=city, state=state,
                                   country=country, location_view=location_view, gender=gender, gender_view=gender_view,
                                   age_view=age_view, web_site=web_site, interests=interests, kind_books=kind_books,
                                   about_me=about_me, active=active)
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
        genre = Genre(name="Fiction")
        genre.save()
        return genre

    @staticmethod
    def generate_book(data):
        book = Book(title=data['title'], sort_by_title=data['sort_by_title'], isbn=data['isbn'],
                    publisher=data['publisher'], published=data['published'], pages=data['pages'],
                    edition=data['edition'], format=data['format'], description=data['description'],
                    edition_language=data['edition_language'], orig_title=data['orig_title'],
                    orig_pub_date=data['orig_pub_date'], media_type=data['media_type'])
        book.save()

    def setUp(self):
        self.create_user_profile("meninleo", "meninleo@gmail.com", "meninleo", "Adrian Mena",
                                 "1990-08-15", "F", "", "Montevideo", "Montevideo", "NZ", "F", "M", "F",
                                 1)
        user = UserProfile.objects.get(pk=1)
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
        self.assertEqual('(#400) Missing one or all required fields, title sort_by_title and authors.',
                         response.data['error']['message'])

    def test_create_book_unauthorized(self):
        self.client.logout()
        payload = json.dumps(self.book_data)
        response = self.client.post(reverse("books-list"), data=payload, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_book_fail_server_error(self):
        self.book_data['edition_language'] = 45
        payload = json.dumps(self.book_data)
        response = self.client.post(reverse("books-list"), data=payload, content_type='application/json')
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)


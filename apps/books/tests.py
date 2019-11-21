import base64
import json
from django.urls import reverse

from rest_framework import status

from apps.accounts.models import UserProfile

from apps.books.models import Genre, Book, BookSeries, BookEdition, Author
from test.base import BaseViewTest


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
        "language": "es",
        "orig_title": "La isla Infinita",
        "orig_pub_date": "2015-01-03",
        "media_type": "B",
        "user_id": 1,
        "series_name": "La isla",
        "series_number": 1,
        "series": 1
    }

    @staticmethod
    def create_series(series_name='Testing cook book'):
        series = BookSeries(name=series_name)
        series.save()
        return series

    @staticmethod
    def create_edition(data, book):
        edition = BookEdition(published=data['published'], publisher=data['publisher'], isbn=data['isbn'],
                              edition=data['edition'], pages=data['pages'], format=data['format'],
                              description=data['description'], language=data['language'], cover=data['cover'],
                              book=book)
        edition.save()
        return edition

    @staticmethod
    def generate_book(data):
        series = BookTests.create_series()
        book = Book(title=data['title'], sort_by_title=data['sort_by_title'], orig_title=data['orig_title'],
                    orig_pub_date=data['orig_pub_date'], media_type=data['media_type'], user_id=data['user_id'],
                    series=series)
        book.save()
        return book

    @staticmethod
    def create_authors(authors=None):
        created = []
        for author in authors:
            author = Author.objects.filter(first_name=author['first_name'], last_name=author['last_name']).first()
            if not author:
                author = Author(first_name=author['first_name'], last_name=author['last_name'], role=author['role'])
                author.save()
            created.append(author)
        return created

    def login(self, user=None):
        if not user:
            user = UserProfile.objects.get(username="meninleo")
        self.token = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION="Goodreads " + self.token["access"])

    def setUp(self):
        self.create_roles()
        self.create_user_profile("meninleo", "meninleo@gmail.com", "meninleo", "Adrian Mena",
                                 "1990-08-15", "F", "", "Montevideo", "Montevideo", "NZ", "F", "M", "F",
                                 1, 1)
        self.create_user_profile("diadokos", "diadokos@gmail.com", "diadokos", "Raul Lopez", "1989-12-05", "F", "",
                                 "Montevideo", "Montevideo", "NZ", "F", "M", "F", 1, 2)
        self.login()

    def test_create_book(self):
        payload = json.dumps(self.book_data)
        response = self.client.post(reverse("book-list"), data=payload, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.book_data['title'], response.data['title'])

    def test_create_book_fail(self):
        response = self.client.post(reverse("book-list"))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('(#400) Missing one or all required fields, title sort_by_title and authors.',
                         response.data['error']['message'])

    def test_create_book_unauthorized(self):
        self.client.logout()
        payload = json.dumps(self.book_data)
        response = self.client.post(reverse("book-list"), data=payload, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_book_fail_value_error(self):
        self.book_data['isbn'] = 'dfrg'
        payload = json.dumps(self.book_data)
        response = self.client.post(reverse("book-list"), data=payload, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_book_partial_update_forbidden(self):
        book = self.generate_book(self.book_data)
        response = self.client.patch(reverse('book-detail', kwargs={'pk': book.id}), {'title': 'NewTitle'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_update_forbidden(self):
        book = self.generate_book(self.book_data)
        response = self.client.put(reverse('book-detail', kwargs={'pk': book.id}), self.book_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_update(self):
        book = self.generate_book(self.book_data)
        self.book_data['title'] = 'El general no tiene quien le escriba cartas'
        self.client.logout()
        user = UserProfile.objects.get(username='diadokos')
        self.login(user)
        self.book_data['user'] = user.id
        response = self.client.put(reverse('book-detail', kwargs={'pk': book.id}), self.book_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, response.data['title'])

    def test_book_partial_update(self):
        book = self.generate_book(self.book_data)
        self.client.logout()
        user = UserProfile.objects.get(username='diadokos')
        self.login(user)
        self.book_data['user'] = user.id
        response = self.client.patch(reverse('book-detail', kwargs={'pk': book.id}),
                                   {'title': 'El general no tiene quien le escriba cartas'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, response.data['title'])

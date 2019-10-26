import tempfile

from django.contrib.auth.hashers import make_password
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile, Role
from apps.books.models import Genre, Book


class BaseViewTest(APITestCase):
    client = APIClient()
    token = {}

    @staticmethod
    def create_roles():
        for type in Role.ROLE_CHOICES:
            role = Role(id=type[0])
            role.save()

    @staticmethod
    def create_user_profile(username, email, password, full_name, birthday, who_can_see_last_name,
                            photo, city, state, country, location_view, gender, gender_view,
                            age_view, role, web_site='', interests='', kind_books='', about_me='', active=True):
        user = UserProfile(username=username, email=email, password=make_password(password), full_name=full_name,
                           birthday=birthday, who_can_see_last_name=who_can_see_last_name, photo=photo, city=city,
                           state=state, country=country, location_view=location_view, gender=gender,
                           gender_view=gender_view, age_view=age_view, web_site=web_site, interests=interests,
                           kind_books=kind_books, about_me=about_me, active=active)
        user.save()
        role_ = Role.objects.get(id=role)
        user.roles.add(role_)

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

    def setUp(self):
        self.create_roles()
        self.create_user_profile("meninleo", "meninleo@gmail.com", "meninleo", "Adrian Mena",
                                 "1990-08-15", "F", "", "Montevideo", "Montevideo", "NZ", "F", "M", "F",
                                 1, 1)
        user = UserProfile.objects.get(pk=1)
        self.token = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION="Goodreads " + self.token["access"])

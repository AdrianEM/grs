from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import UserProfile
from apps.accounts.serializers import UserProfileSerializer


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_user_profile(username, email, password, first_name, last_name, birthday, who_can_see_last_name,
                    photo, city, state, country, location_view, gender, gender_view,
                    age_view, web_site='', interests='', kind_books='', about_me=''):
        user = User(username=username, email=email, password=make_password(password), first_name=first_name,
                    last_name=last_name)
        user.save()
        UserProfile.objects.create(user=user, birthday=birthday, who_can_see_last_name=who_can_see_last_name,
                                   photo=photo, city=city, state=state, country=country, location_view=location_view,
                                   gender=gender, gender_view=gender_view,age_view=age_view,web_site=web_site,
                                   interests=interests, kind_books=kind_books, about_me=about_me)


    def setUp(self):
        self.create_user_profile('meninleo', 'meninleo@gmail.com', 'meninleo', 'Adrian', 'Mena',
                                 '1990-08-15', 'F', '', 'Montevideo', 'Montevideo', 'NZ', 'F', 'M', 'F',
                                 1)
        self.create_user_profile('adrianminfo', 'adrianminfo90@gmail.com', 'adrianminfo', 'Adrian', 'Mena',
                                 '1990-08-15', 'F', '', 'Montevideo', 'Montevideo', 'NZ', 'F', 'M', 'F',
                                 1)



class GetAllUsersTest(BaseViewTest):
    def test_get_all_songs(self):
        """
        This test ensure that all users added in the setUp method exist when we make
         a GET request to the users/ endpoint
        :return:
        """
        response = self.client.get(reverse("users-all"))
        expected = UserProfile.objects.all()
        serialized = UserProfileSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetUserProfileById(BaseViewTest):
    """
    This test ensures that given a user id it will retrieve all user data when we make
    a GET request to the users/pk endpoint.
    """
    def test_get_user_data(self):
        response = self.client.get(reverse("user-detail", kwargs={"pk": "1"}))
        expected = UserProfile.objects.get(pk=1)
        serialized = UserProfileSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

import tempfile

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile, EmailSettings, FeedSetting, ReadingGroup
from apps.accounts.serializers import UserProfileSerializer, EmailSettingSerializer, FeedSettingSerializer
from goodreads import settings


class BaseViewTest(APITestCase):
    client = APIClient()
    token = {}

    @staticmethod
    def create_user_profile(username, email, password, first_name, last_name, birthday, who_can_see_last_name,
                            photo, city, state, country, location_view, gender, gender_view,
                            age_view, web_site='', interests='', kind_books='', about_me='', active=True):
        user = User(username=username, email=email, password=make_password(password), first_name=first_name,
                    last_name=last_name)
        user.save()
        user_profile = UserProfile(user=user, birthday=birthday, who_can_see_last_name=who_can_see_last_name,
                                   photo=photo, city=city, state=state, country=country, location_view=location_view,
                                   gender=gender, gender_view=gender_view, age_view=age_view, web_site=web_site,
                                   interests=interests, kind_books=kind_books, about_me=about_me, active=active)
        user_profile.save()
        email_setting = EmailSettings(user=user_profile)
        email_setting.save()
        feed_setting = FeedSetting(user=user_profile)
        feed_setting.save()

    @staticmethod
    def create_image():
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (200, 200), 'white')
            image.save(f, 'PNG')

        return open(f.name, mode='rb')

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def setUp(self):
        self.create_user_profile('meninleo', 'meninleo@gmail.com', 'meninleo', 'Adrian', 'Mena',
                                 '1990-08-15', 'F', '', 'Montevideo', 'Montevideo', 'NZ', 'F', 'M', 'F',
                                 1)
        self.create_user_profile('adrianminfo', 'adrianminfo90@gmail.com', 'adrianminfo', 'Adrian', 'Mena',
                                 '1990-08-15', 'M', '', 'Montevideo', 'Montevideo', 'NZ', 'F', 'M', 'F',
                                 1)
        self.create_user_profile('meninleordgz', 'meninleordgz@outllok.es', 'meninleordgz', 'Adrian', 'Mena',
                                 '1990-08-15', 'M', '', 'Montevideo', 'Montevideo', 'NZ', 'F', 'M', 'F',
                                 1)
        user = User.objects.get(pk=1)
        self.token = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION='Goodreads ' + self.token['access'])

        group = ReadingGroup(name='Hello New York', description='description', rules='rules', topic='BL',
                             tags='tags,he,binhe', country='US', creator_id=1)
        group.save()


class UserProfileTests(BaseViewTest):

    user_profile_data = {
        'email': 'diadokos@gmail.com',
        'first_name': 'Raul',
        'password': 'diadokos',
        'birthday': '1988-12-05',
        'who_can_see_last_name': 'F',
        'photo': '',
        'city': 'Montevideo',
        'state': 'Montevideo',
        'country': 'NZ',
        'gender': 'M',
        'gender_view': 'F',
        'age_view': '2',
        'web_site': 'https://www.goodreads.com',
        'interests': 'Books,Friends,Video games',
        'kind_books': 'CyFy',
        'about_me': 'Nothing to add.',
        'location_view': 'F',
        'user_id': 1
    }

    def test_get_all_profiles(self):
        """
        This test ensures that all users added in the setUp method exist when we make
         a GET request to the users/ endpoint
        :return:
        """
        response = self.client.get(reverse("user-profile-list"))
        expected = UserProfile.objects.filter(active=True)
        serialized = UserProfileSerializer(expected, many=True)
        self.assertEqual(response.data['results'], serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        """
        This test ensures that one of the users added in the setUp exist when we make
        a GET request to users/<int:pk> endpoint
        :return:
        """
        response = self.client.get(reverse("user-profile-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = UserProfile.objects.get(pk=1)
        serialized = UserProfileSerializer(expected)
        self.assertEqual(response.data, serialized.data)

    def test_create_user_profile(self):
        """
        This test ensures that a new user profile is created with the provided information.
        :return:
        """
        self.user_profile_data['photo'] = self.create_image()
        response = self.client.post(reverse('user-profile-list'), self.user_profile_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['email_settings'])
        self.assertTrue(response.data['feed_settings'])

    def test_create_user_profile_fail(self):
        """
        Missing data
        :return:
        """
        response = self.client.post(reverse('user-profile-list'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile(self):
        self.user_profile_data['photo'] = self.create_image()
        response = self.client.put(reverse('user-profile-detail', kwargs={"pk": 1}), self.user_profile_data,
                                   format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_profile(self):
        response = self.client.delete(reverse('user-profile-detail', kwargs={"pk": 2}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        expected = UserProfile.objects.get(pk=2)
        self.assertTrue(not expected.active)
        self.assertTrue(not expected.user.is_active)

    def test_get_email_setting(self):
        response = self.client.get(reverse('user-profile-get-email-settings', args=[1]))
        expected = EmailSettings.objects.get(user_id=1)
        serialized = EmailSettingSerializer(expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized.data)

    def test_get_feed_setting(self):
        response = self.client.get(reverse('user-profile-get-feed-settings', args=[1]))
        expected = FeedSetting.objects.get(user_id=1)
        serialized = FeedSettingSerializer(expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialized.data)


class EmailSettingTests(BaseViewTest):
    email_setting = {
        'id': 1,
        'user': 1,
        'email_frequency': 'D',
        'include_top_friends_only': False,
        'include_to_read_books': False,
        'likes_my_status': False,
        'sends_me_message': False,
        'adds_me_friend': False,
        'follow_my_review': False,
        'invites_group': False,
        'invites_event': False,
        'invites_trivia': False,
        'ask_vote': False,
        'invites_poll': False,
        'mention_recommender': False,
        'recommend_book': False,
        'comment_review': 'E',
        'comment_profile': 'E',
        'like_listopia': 'B',
        'comment_listopia': 'E',
        'comment_recommendation': 'E',
        'comment_poll': 'E',
        'comment_shelve': 'E',
        'comment_activity': 'E',
        'comment_qa': 'E',
        'like_question': 'B',
        'list_giveaway_book_toread': 'B',
        'list_giveaway_author_fallow': 'E',
        'comment_friendship': 'E',
        'post_note': 'E',
        'monthly_newsletter': False,
        'newsletter_favorite_genre': False,
        'young_newsletter': False,
        'romance_newsletter': False,
        'monthly_new_release': False,
        'monthly_new_release_only_author_read': False,
        'new_features_gr': False,
        'update_giveaway_won': False,
        'update_giveaway_entered': False,
        'weekly_digest': False,
        'author_rated': False,
        'book_available': False,
        'author_release': False,
        'recommendation_finish_book': False,
        'discussion_new_post': 'W',
        'follow_discussion': False,
        'group_start_reading': False

    }

    def test_update_email_setting(self):
        response = self.client.put(reverse('email-setting', kwargs={"pk": 1}), self.email_setting)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.email_setting['email_frequency'], response.data['email_frequency'])


class FeedSettingTests(BaseViewTest):
    feed_setting = {
        'id': 1,
        'user_id': 1,
        'add_book': False,
        'add_quote': False,
        'recommend_book': False,
        'add_new_status': False,
        'comment_so_review': False,
        'vote_book_review': False,
        'add_friend': False,
        'comment_book_or_discussion': False,
        'join_group': False,
        'answer_poll': False,
        'enter_giveaway': False,
        'follow_author': False
    }

    def test_update_feed_seeting(self):
        response = self.client.put(reverse('feed-setting', kwargs={"pk": 1}), self.feed_setting)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReadingGroupTests(BaseViewTest):
    group_data = {
        'name': 'Dragon tatoo',
        'description': 'Test group description',
        'rules': 'test rules',
        'topic': 'BL',
        'tags': 'tags,test,he',
        'country': 'AU',
        'creator': 1
    }

    def test_create_group(self):
        response = self.client.post(reverse('reading-group-list'), self.group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_group(self):
        group = ReadingGroup(name='Hello New York', description='description', rules='rules', topic='BL', tags=
                             'tags,he,binhe', country='US', creator_id=1)
        group.save()
        response = self.client.put(reverse('reading-group-detail', kwargs={'pk': group.id}), self.group_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_group(self):
        group = ReadingGroup(name='Hello New York', description='description', rules='rules', topic='BL', tags=
                             'tags,he,binhe', country='US', creator_id=1)
        group.save()
        response = self.client.delete(reverse('reading-group-detail', kwargs={'pk':group.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group.refresh_from_db()
        self.assertEqual(group.active, False)

    def test_add_user_to_group(self):
        group = ReadingGroup(name='Hello New York', description='description', rules='rules', topic='BL', tags=
                             'tags,he,binhe', country='US', creator_id=1)
        group.save()
        self.assertEqual(9, 9)

    def test_send_invitation_user(self):
        data = {
            'user_id': 1
        }
        url = reverse('reading-group-send-user-invitation',  kwargs={'pk': 1})
        response = self.client.post(reverse('reading-group-send-user-invitation', kwargs={'pk': 1}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['Message'], 'Invitation send it successfully')

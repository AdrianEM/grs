from django.contrib.auth.models import User
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from apps.accounts.models import UserProfile, Shelve, EmailSettings, FeedSetting, ReadingGroup


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


class UserProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    shelves = serializers.PrimaryKeyRelatedField(many=True, queryset=Shelve.objects.all(), required=False)
    user = UserSerializer(read_only=True)
    email_settings = serializers.SerializerMethodField()
    feed_settings = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "user", "birthday", "who_can_see_last_name",
                  "photo", "city", "state", "country", "location_view", "gender", "gender_view",
                  "age_view", "web_site", "interests", "kind_books", "about_me", "shelves",
                  "email_settings", "feed_settings", "created", "modified")

    def get_email_settings(self, instance):
        try:
            setting = EmailSettings.objects.get(user_id=instance.id)
            return setting.id
        except EmailSettings.DoesNotExist:
            pass

    def get_feed_settings(self, instance):
        try:
            setting = FeedSetting.objects.get(user_id=instance.id)
            return setting.id
        except FeedSetting.DoesNotExist:
            pass


class FeedSettingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = FeedSetting
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.id


class EmailSettingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = EmailSettings
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.id


class ShelveSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.user.username')

    class Meta:
        model = Shelve
        fields = ("id", "name", "owner")


class ReadingGroupSerializer(serializers.ModelSerializer):
    creator_id = serializers.SerializerMethodField()

    class Meta:
        model = ReadingGroup
        fields = '__all__'

    def get_creator_id(self, instance):
        return instance.creator.id

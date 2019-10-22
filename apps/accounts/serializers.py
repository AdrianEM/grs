from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from apps.accounts.models import UserProfile, EmailSettings, FeedSetting, ReadingGroup, ReadingGroupEmailSetting, Role
from apps.books.models import Shelve


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id']


class UserProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    shelves = serializers.PrimaryKeyRelatedField(many=True, queryset=Shelve.objects.all(), required=False)
    email = serializers.SerializerMethodField()
    email_settings = serializers.SerializerMethodField()
    feed_settings = serializers.SerializerMethodField()
    group_email_settings = serializers.SerializerMethodField()
    role = RoleSerializer(read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = ("id", "full_name", "birthday", "email", "who_can_see_last_name",
                  "photo", "city", "state", "country", "location_view", "gender", "gender_view",
                  "age_view", "web_site", "interests", "kind_books", "about_me", "shelves",
                  "email_settings", "feed_settings", "created", "modified", "group_email_settings", "role")

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

    def get_group_email_settings(self, instance):
        try:
            setting_query = ReadingGroupEmailSetting.objects.filter(user_id=instance.id)
            settings_id = []
            for setting in setting_query:
                settings_id.append(setting.id)
            return settings_id
        except Exception:
            pass

    def get_email(self, instance):
        return instance.email


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

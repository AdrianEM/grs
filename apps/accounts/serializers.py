from rest_framework import serializers

from apps.accounts.models import UserProfile, Shelve


class UserProfileSerializer(serializers.ModelSerializer):
    shelves = serializers.PrimaryKeyRelatedField(many=True,queryset=Shelve.objects.all())

    class Meta:
        model = UserProfile
        fields = ("id", "birthday", "who_can_see_last_name",
                  "photo", "city", "state", "country", "location_view", "gender", "gender_view",
                  "age_view", "web_site", "interests", "kind_books", "about_me", "shelves")


class ShelveSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Shelve
        fields = ("id", "name", "owner")
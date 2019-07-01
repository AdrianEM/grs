from django.contrib import admin

from apps.accounts.models import UserProfile, Shelve

admin.site.register(UserProfile)
admin.site.register(Shelve)

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.accounts.views import UsersProfileViewSet, EmailSettingView, FeedSettingView, ReadingGroupViewSet, \
    create_user_profile

router = DefaultRouter()
router.register(r'user-profile', UsersProfileViewSet, basename='user-profile')
router.register(r'reading-group', ReadingGroupViewSet, basename='reading-group')

urlpatterns = [
    path(r'user', create_user_profile, name='user-profile-create'),
    path(r'email-setting/<int:pk>', EmailSettingView.as_view(), name='email-setting'),
    path(r'feed-setting/<int:pk>', FeedSettingView.as_view(), name='feed-setting')
]

urlpatterns += router.urls


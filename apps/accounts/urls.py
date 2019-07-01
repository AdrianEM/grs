from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.accounts.views import UsersProfileViewSet, EmailSettingView, FeedSettingView, ReadingGroupViewSet

router = DefaultRouter()
router.register(r'user-profile', UsersProfileViewSet, basename='user-profile')
router.register(r'reading-group', ReadingGroupViewSet, basename='reading-group')

urlpatterns = [
    path(r'email-setting/<int:pk>', EmailSettingView.as_view(), name='email-setting'),
    path(r'feed-setting/<int:pk>', FeedSettingView.as_view(), name='feed-setting'),
    path(r'reading-group/<int:pk>/accept-group-invitation/<str:uidb64>/<str:token>',
         ReadingGroupViewSet.as_view({'post': 'accept-group_invitation'}), name='accept-group-invitation')
]

urlpatterns += router.urls


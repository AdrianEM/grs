from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from apps.accounts.views import UsersProfileView, UserProfileDetail

urlpatterns = [
    path('', UsersProfileView.as_view(), name="users-all"),
    path('<int:pk>', UserProfileDetail.as_view(), name="user-detail")
]

urlpatterns = format_suffix_patterns(urlpatterns)

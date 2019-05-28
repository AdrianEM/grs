from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile, Shelve
from apps.accounts.serializers import UserProfileSerializer, ShelveSerializer


class UsersProfileView(generics.ListCreateAPIView):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetail(APIView):

    def get_object(self, pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class ShelvesView(generics.ListCreateAPIView):
    queryset = Shelve.objects.all()
    serializer_class = ShelveSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

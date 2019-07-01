from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail

from django.http import Http404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile, Shelve, EmailSettings, FeedSetting, ReadingGroup, ReadingGroupUsers
from apps.accounts.serializers import UserProfileSerializer, ShelveSerializer, EmailSettingSerializer, \
    FeedSettingSerializer, ReadingGroupSerializer
from apps.utils.utils import group_invitation_token


class UsersProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        users_profile = UserProfile.objects.filter(active=True)
        paginated = self.paginate_queryset(users_profile)
        serialized = UserProfileSerializer(paginated, many=True)
        return self.get_paginated_response(serialized.data)

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        first_name = request.data.get('first_name', None)
        if email and password and first_name:
            user = User(username=email, email=request.data['email'], password=make_password(password),
                        first_name=first_name)
            user.save()
            user_profile = UserProfile(user=user)
            user_profile.save()
            email_setting = EmailSettings(user=user_profile)
            email_setting.save()
            feed_setting = FeedSetting(user=user_profile)
            feed_setting.save()
            self.create_default_shelves(user_profile)
            serialized = UserProfileSerializer(user_profile)
            return Response(data=serialized.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"Status": 'error',
                        'Message': 'Some of the information pieces were not provided(email,password or first name)'})

    def update(self, request, *args, **kwargs):
        user_id = request.data.get('user_id', None)
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
                    "message": "(#400) Can't find the user profile.",
                    "code": 400
                }})
            email = request.data.get('email', None)
            password = request.data.get('password', None)
            first_name = request.data.get('first_name', None)
            last_name = request.data.get('last_name', None)
            if email:
                email_already_exist = User.objects.filter(email=email)
                if len(email_already_exist) > 0 and user.email != email:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
                        "message": "(#400) The email provided belongs to another account.",
                        "code": 400
                    }})
                user.email = email
            if password:
                user.set_password(password)
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save()
        return super(UsersProfileViewSet, self).update(request)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if pk:
            try:
                user_profile = UserProfile.objects.get(pk=pk)
            except UserProfile.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
                    "message": "(#400) Doesn't exist the user you are looking for.",
                    "code": 400
                }})
            user_profile.active = False
            user_profile.save()
            user_profile.user.is_active = False
            user_profile.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_default_shelves(user_profile):
        if user_profile:
            default_shelves_name = ['read', 'to-read', 'currently-reading']
            for shelve_name in default_shelves_name:
                shelve = Shelve(name=shelve_name, owner=user_profile)
                shelve.save()

    @action(detail=True, methods=['get'], url_name='get-email-settings')
    def email_setting(self, request, *args, **kwargs):
        user_id = kwargs.get('pk', None)
        if user_id:
            try:
                setting = EmailSettings.objects.get(user_id=user_id)
            except EmailSettings.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
                    'message': 'Email settings doesn\'t exist for this account.'
                }})
            serialized = EmailSettingSerializer(setting)
            return Response(status=status.HTTP_200_OK, data=serialized.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
            'message': 'Malformed url.'
        }})

    @action(detail=True, methods=['get'], url_name='get-feed-settings')
    def feed_setting(self, request, *args, **kwargs):
        user_id = kwargs.get('pk', None)
        if user_id:
            try:
                setting = FeedSetting.objects.get(user_id=user_id)
            except FeedSetting.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
                    'message': 'Feed settings doesn\'t exist for this account.'
                }})
            serialized = FeedSettingSerializer(setting)
            return Response(status=status.HTTP_200_OK, data=serialized.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
            'message': 'Malformed url.'
        }})


class EmailSettingView(generics.UpdateAPIView):
    queryset = EmailSettings.objects.all()
    serializer_class = EmailSettingSerializer
    permission_classes = (IsAuthenticated,)


class FeedSettingView(generics.UpdateAPIView):
    queryset = FeedSetting.objects.all()
    serializer_class = FeedSettingSerializer
    permission_classes = (IsAuthenticated,)


class ShelvesView(generics.ListCreateAPIView):
    queryset = Shelve.objects.all()
    serializer_class = ShelveSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReadingGroupViewSet(viewsets.ModelViewSet):
    queryset = ReadingGroup.objects.all()
    serializer_class = ReadingGroupSerializer
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if pk:
            try:
                group = ReadingGroup.objects.get(pk=pk)
            except ReadingGroup.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND, data={'Status': 'error', 'Message': 'Can\'t find the '
                                                                                                      'group'})
            group.active = False
            group.save()
            return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='send-user-invitation', url_path='group-user-invitation')
    def send_user_invitation(self, request, *args, **kwargs):
        try:
            current_user = UserProfile.objects.get(user=request.user)
            group_id = kwargs.get('pk', None)
            if group_id:
                group = ReadingGroup.objects.get(pk=group_id)
                user_to_invite_id = request.data.get('user_id', None)
                if user_to_invite_id:
                    user_to_invite = UserProfile.objects.get(pk=user_to_invite_id)
                    reading_group_user = ReadingGroupUsers(user=user_to_invite, group=group, who_invites=current_user)
                    reading_group_user.save()
                    data = {
                        'user_name': user_to_invite.user.first_name,
                        'group_name': group.name,
                        'pk': group.id,
                        'who_invites': current_user.user.get_full_name(),
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(current_user.id)),
                        'token': group_invitation_token.make_token(request.user)
                    }
                    body = render_to_string('emails/group_invitation.html', data)
                    email = EmailMessage(_('Invitation'), body, to=[user_to_invite.user.email])
                    email.content_subtype = 'html'
                    email.send()
                    return Response(status=status.HTTP_200_OK, data={'Status': 'success',
                                                                     'Message': 'Invitation send it successfully'})
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'Status': 'error',
                                                                          'Message': _('Has to provide a user id')})
        except ReadingGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'Status': 'error', 'Message': _('Reading group not found')})

        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'Status': 'error', 'Message': _('User not found')})

    @action(detail=True, methods=['put'], url_name='accept-group-invitation', url_path='user-group-invitation')
    def accept_group_invitation(self, request, *args, **kwargs):
        try:
            uid = kwargs.get('uidb64', None)
            group_id = kwargs.get('pk', None)
            user = UserProfile.objects.get(pk=urlsafe_base64_decode(uid))
            group = ReadingGroup.objects.get(pk=group_id)
        except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist, ReadingGroup.DoesNotExist):
            user = None
            group = None
        if user is not None and group is not None:
            token = kwargs.get('token', None)
            if group_invitation_token.check_token(request.user, token):
                readin_group_user = ReadingGroupUsers.objects.filter(group_id=group_id, user_id=user.id)
                for rgu in readin_group_user:
                    rgu.active = True
                    rgu.invitation_answered = True
                    rgu.save()
                    return Response(status=status.HTTP_200_OK, data={'Status': 'success',
                                                                     'Message': _('Invitation accepted')})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'Status': 'error', })


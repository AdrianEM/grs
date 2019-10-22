from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from apps.accounts.models import UserProfile, EmailSettings, FeedSetting, ReadingGroup, ReadingGroupUsers, \
    ReadingGroupEmailSetting, Role
from apps.accounts.serializers import UserProfileSerializer, ShelveSerializer, EmailSettingSerializer, \
    FeedSettingSerializer, ReadingGroupSerializer
from apps.books.models import Shelve


@api_view(['POST'])
def create_user_profile(request):
    try:
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        full_name = request.data.get('full_name', None)
        if email and password and full_name:
            role = Role.objects.get(pk=Role.READER)
            user = UserProfile(username=email, email=email, password=make_password(password),
                               first_name=full_name)
            user.save()
            user.roles.add(role)
            UserProfile.objects.create_default_shelves(user)
            serialized = UserProfileSerializer(user)
            return Response(data=serialized.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"Status": 'error',
                                                                  'Message': 'Some information pieces were not'
                                                                             ' provided(email,password or first name)'})
    except Role.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data={'Status': 'error', 'Message': 'Can\'t find the role.'})

    except Exception as ex:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": {
            "message": "(#500) {}.".format(_('Server error')), "code": 400
        }})


class IsFeedOrEmailSettingOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True
        return False


class IsFeedOrEmailSettingOwnerExtraAction(permissions.BasePermission):

    def has_permission(self, request, view):
        if str(request.user.email_setting.id) == view.kwargs.get('pk', None):
            return True
        return False


class IsShelveOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj or any(role.id == Role.ADMIN or role.id == Role.STAFF for role in request.user.roles):
            return True
        return False


# TODO: test this
class IsReadingGroupAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user == obj.creator or \
                obj.reading_group_users.filter(user=request.user, is_admin=True).exists():
            return True
        return False


# TODO: how  to handle permissions
class UsersProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    http_method_names = ['get', 'patch', 'put', 'delete']

    def get_permissions(self):
        setting_actions = ['email_setting', 'feed_setting']
        actions_for_is_authenticated = ['list', 'accept_group_invitation']
        if self.action in setting_actions:
            permission_classes = [IsFeedOrEmailSettingOwnerExtraAction]
        elif self.action in actions_for_is_authenticated:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    # def partial_update(self, request, *args, **kwargs):
    #     user_id = kwargs.get('pk', None)
    #     if user_id:
    #         try:
    #             user = UserProfile.objects.get(pk=user_id)
    #         except User.DoesNotExist:
    #             return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
    #                 "message": "(#400) Can't find the user profile.",
    #                 "code": 400
    #             }})
    #         email = request.data.get('email', None)
    #         password = request.data.get('password', None)
    #         first_name = request.data.get('first_name', None)
    #         last_name = request.data.get('last_name', None)
    #         should_update = False
    #         if email:
    #             if UserProfile.objects.exist_email(email, user):
    #                 return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
    #                     "message": "(#400) The email provided belongs to another account.",
    #                     "code": 400
    #                 }})
    #             user.email = email
    #             should_update = True
    #         if password:
    #             user.set_password(password)
    #             should_update = True
    #         if first_name:
    #             user.first_name = first_name
    #             should_update = True
    #         if last_name:
    #             user.last_name = last_name
    #             should_update = True
    #         if should_update:
    #             user.save()
    #     return super(UsersProfileViewSet, self).partial_update(request)

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
            user_profile.is_active = False
            user_profile.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_name='get-email-settings')
    def email_setting(self, request, *args, **kwargs):
        user_id = kwargs.get('pk', None)
        if user_id:
            try:
                settings = UserProfile.objects.get_email_settings(user_id)
            except EmailSettings.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
                    'message': 'Email settings doesn\'t exist for this account.'
                }})
            serialized = EmailSettingSerializer(settings)
            return Response(status=status.HTTP_200_OK, data=serialized.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
            'message': 'Malformed url.'
        }})

    @action(detail=True, methods=['get'], url_name='get-feed-settings')
    def feed_setting(self, request, *args, **kwargs):
        user_id = kwargs.get('pk', None)
        if user_id:
            try:
                settings = UserProfile.objects.get_feed_settings(user_id)
            except FeedSetting.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
                    'message': 'Feed settings doesn\'t exist for this account.'
                }})
            serialized = FeedSettingSerializer(settings)
            return Response(status=status.HTTP_200_OK, data=serialized.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': {
            'message': 'Malformed url.'
        }})

    @action(detail=True, methods=['put'], url_name='accept-group-invitation',
            url_path='user-group-invitation')
    def accept_group_invitation(self, request, *args, **kwargs):
        try:
            group_id = kwargs.get('pk', None)
            user_id = request.data.get('userId', None)
            user = UserProfile.objects.get(pk=user_id)
            group = ReadingGroup.objects.get(pk=group_id)

            reading_group_user = ReadingGroupUsers.objects.filter(group=group, user=user).first()
            if reading_group_user and not reading_group_user.active:
                reading_group_user.active = True
                reading_group_user.invitation_answered = True
                reading_group_user.save()
                reading_group_email_setting = ReadingGroupEmailSetting(group=group, user=user)
                reading_group_email_setting.save()
                return Response(status=status.HTTP_200_OK, data={'Status': 'success',
                                                                 'Message': _('Invitation accepted')})

            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'Status': 'error',
                                  'Message': _('User hasn\'t been invited to be part of this group.')})
        except (UserProfile.DoesNotExist, ReadingGroup.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'Status': 'error', 'Message': 'Check user and group.'})


class EmailSettingView(generics.UpdateAPIView):
    queryset = EmailSettings.objects.all()
    serializer_class = EmailSettingSerializer
    permission_classes = (IsAuthenticated, IsFeedOrEmailSettingOwner)


class FeedSettingView(generics.UpdateAPIView):
    queryset = FeedSetting.objects.all()
    serializer_class = FeedSettingSerializer
    permission_classes = (IsAuthenticated, IsFeedOrEmailSettingOwner)


class ShelvesView(generics.ListCreateAPIView):
    queryset = Shelve.objects.all()
    serializer_class = ShelveSerializer
    permission_classes = (IsAuthenticated, IsShelveOwner)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReadingGroupViewSet(viewsets.ModelViewSet):
    queryset = ReadingGroup.objects.all()
    serializer_class = ReadingGroupSerializer

    def get_permissions(self):
        admin_actions = ['destroy', 'create_user_invitation', 'update']
        if self.action in admin_actions:
            permission_classes = [IsReadingGroupAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if pk:
            try:
                group = ReadingGroup.objects.get(pk=pk)
                self.check_object_permissions(request, group)
            except ReadingGroup.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND, data={'Status': 'error', 'Message': 'Can\'t find the '
                                                                                                      'group'})
            except PermissionError:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'Status': 'error', 'Message': 'Forbidden'})
            group.active = False
            group.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_name='create-user-invitation', url_path='group-user-invitation')
    def create_user_invitation(self, request, *args, **kwargs):
        try:
            current_user = UserProfile.objects.get(pk=request.user.id)
            group_id = kwargs.get('pk', None)
            user_to_invite_id = request.data.get('user_id', None)
            if group_id and user_to_invite_id:
                group = ReadingGroup.objects.get(pk=group_id)
                self.check_object_permissions(request, group)
                user_to_invite = UserProfile.objects.get(pk=user_to_invite_id)
                if not ReadingGroupUsers.objects.filter(user_id=user_to_invite_id, group_id=group_id).exists():
                    reading_group_user = ReadingGroupUsers(user=user_to_invite, group=group, who_invites=current_user)
                    reading_group_user.save()

                return Response(status=status.HTTP_200_OK, data={'Status': 'success',
                                                                 'Message': 'Invitation successfully created'})
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'Status': 'error',
                                                                      'Message': _('Has to provide a user and group id')})
        except ReadingGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'Status': 'error', 'Message': _('Reading group not found')})

        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'Status': 'error', 'Message': _('User not found')})

        except PermissionError:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'Status': 'error', 'Message': 'Forbidden'})



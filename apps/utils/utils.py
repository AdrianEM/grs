from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class GroupTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.first_name)
        )


group_invitation_token = GroupTokenGenerator()

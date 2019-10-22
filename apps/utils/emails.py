# Functions to process emails
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


def send_email(template, data, to):
    body = render_to_string(template, data)
    email = EmailMessage(_('Invitation'), body, to=to)
    email.content_subtype = 'html'
    email.send()

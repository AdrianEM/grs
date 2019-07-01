# Functions to process emails
from django.core.mail import send_mail


def send_email(from_, to, body, subject):
    send_mail(subject, body, from_, to, fail_silently=False)

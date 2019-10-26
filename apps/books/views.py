import json

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.books.models import Book, Author, BookAuthor, BookMetadata
from apps.books.serializers import BookSerializer


class IsLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        if any(role.id == Role.LIBRARIAN for role in request.user.roles.all()):
            return True
        return False


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'put']

    def get_permissions(self):
        permissions_classes = [IsAuthenticated]
        librarian_actions = ['update', 'partial_update']
        if self.action in librarian_actions:
            permissions_classes.append(IsLibrarian)
        return [permission() for permission in permissions_classes]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            title = request.data.get('title', None)
            sort_by_title = request.data.get('sort_by_title', None)
            authors = request.data.get('authors', None)
            if title is None or sort_by_title is None or authors is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
                    "message": "(#400) {}.".format(
                        _('Missing one or all required fields, title sort_by_title and authors')),
                    "code": 400
                }})
            isbn = request.data.get('isbn', '')
            publisher = request.data.get('publisher', '')
            published = request.data.get('published', None)
            pages = request.data.get('pages', None)
            format_ = request.data.get('format', 'PB')
            description = request.data.get('description', '')
            language = request.data.get('language', 'en')
            orig_title = request.data.get('orig_title', '')
            orig_pub_date = request.data.get('orig_pub_date', '')
            media_type = request.data.get('media_type', '')
            book = Book(title=title, sort_by_title=sort_by_title, isbn=isbn, publisher=publisher, published=published,
                        pages=pages, format=format_, description=description, edition_language=language,
                        orig_title=orig_title, orig_pub_date=orig_pub_date, media_type=media_type, user=request.user)
            book.save()
            for author in authors:
                first_name = author.get('first_name', '')
                last_name = author.get('last_name', '')
                role = author.get('role', 'AU')
                if not first_name:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
                        "message": "(#400) {}.".format(
                            _('Missing author\'s name')),
                        "code": 400
                    }})
                author = Author.objects.filter(first_name=first_name, last_name=last_name).first()
                if not author:
                    author = Author(first_name=first_name, last_name=last_name, role=role)
                    author.save()
                if not BookAuthor.objects.filter(author=author, book=book).exists():
                    book_author = BookAuthor.objects.create(author=author, book=book)
                    book_author.save()
            book_metadata = BookMetadata(book=book, user=request.user)
            book_metadata.save()
            serialized = BookSerializer(book)
            return Response(status=status.HTTP_201_CREATED, data=serialized.data)
        except ValueError as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": {
                "message": "(#400) {}.".format(ex.__str__()), "code": 400
            }})

        except Exception as ex:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={"message": "(#500) {}.".format(_('Server error'))})

    @action(detail=True, methods=['put'], url_name='combine-books')
    def combine_books(self, request, *args, **kwargs):
        pass

    @action(detail=True, methods=['put'], url_name='merge-books')
    def merge_books(self, request, *args, **kwargs):
        pass

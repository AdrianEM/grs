import json

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.books.models import Book, Author, BookAuthor, BookMetadata, BookSeries, BookEdition
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
        librarian_actions = ['update', 'partial_update', 'combine_books', 'merge_books']
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
            edition = BookEdition.objects.filter(isbn=isbn).first()
            if edition and isbn:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'message': _('This book edition already exists')})
            series_name = request.data.get('series_name', '')
            series_number = request.data.get('series_number', '')
            if series_name and not series_number:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'message': _('If you specified a series name you have to provide a series'
                                                   ' number.')})
            if isbn and series_name:
                book_series_number_exists = Book.objects.filter(title__exact=title, series__name__exact=series_name,
                                                                series_number=series_number).count()
                if book_series_number_exists > 0:
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data={'message': _('This book edition already exists.')})
            series = BookSeries.objects.filter(name__exact=series_name).first()
            if not series and series_name:
                series = BookSeries(name=series_name)
                series.save()
            orig_title = request.data.get('orig_title', '')
            orig_pub_date = request.data.get('orig_pub_date', '')
            media_type = request.data.get('media_type', '')

            book = Book(title=title, sort_by_title=sort_by_title, orig_title=orig_title,
                        series_number=series_number, series=series, orig_pub_date=orig_pub_date,
                        media_type=media_type, user=request.user)
            publisher = request.data.get('publisher', '')
            published = request.data.get('published', None)
            pages = request.data.get('pages', None)
            format_ = request.data.get('format', 'PB')
            description = request.data.get('description', '')
            language = request.data.get('language', 'en')
            cover = request.data.get('cover', '')
            edition = BookEdition(publisher=publisher, published=published, pages=pages, format=format_,
                                  description=description, language=language, isbn=isbn, cover=cover)
            first_author = None
            authors_objs = []
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
                authors_objs.append(author)
                if not first_author:
                    first_author = author
            book.save()
            edition.book = book
            edition.save()
            for author in authors_objs:
                if not BookAuthor.objects.filter(author=author, book=book).exists():
                    if not first_author:
                        book_author = BookAuthor.objects.create(author=author, book=book, primary_author=author)
                    else:
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

    def partial_update(self, request, *args, **kwargs):
        field_to_change = request.data.get('user_id', None)
        if field_to_change:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={"message": _("It's forbidden to modify the user who created the book")})
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['put'], url_name='combine-books')
    def combine_books(self, request, *args, **kwargs):
        """
        Allows combine two different editions from the same book
        """
        pass

    @action(detail=True, methods=['put'], url_name='merge-books')
    def merge_books(self, request, *args, **kwargs):
        pass

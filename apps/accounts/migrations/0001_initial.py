# Generated by Django 2.2.1 on 2019-05-28 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('birthday', models.DateField(db_column='Birthday', help_text="User's birthday.")),
                ('who_can_see_last_name', models.CharField(choices=[('F', 'Friends only'), ('E', 'Everyone'), ('No', 'No one')], max_length=2)),
                ('photo', models.ImageField(blank=True, db_column='Photo', help_text="User's profile image.", upload_to='')),
                ('city', models.CharField(blank=True, db_column='City', help_text="User's city", max_length=70)),
                ('state', models.CharField(db_column='State', help_text="User's state/province.", max_length=70)),
                ('country', django_countries.fields.CountryField(help_text="User's country", max_length=2)),
                ('location_view', models.CharField(choices=[('F', 'Friends only'), ('E', 'Everyone'), ('No', 'No one')], help_text="Who can see user's location.", max_length=2)),
                ('gender', models.CharField(choices=[('F', 'Female'), ('M', 'Male'), ('X', 'X')], help_text="User's gender.", max_length=2)),
                ('gender_view', models.CharField(choices=[('F', 'Friends only'), ('E', 'Everyone'), ('No', 'No one')], help_text="Who can see user's gender", max_length=2)),
                ('age_view', models.CharField(choices=[(1, 'Age & birthday to Goodreads members'), (2, 'Age to Goodreads members, birthday to friends'), (3, 'Age to Goodreads members, birthday to no one'), (4, 'Age and birthday to friends'), (5, 'Age to friends, birthday to no one'), (6, 'Age and birthday to no one'), (7, 'Age to no one, birthday to Goodreads members'), (8, 'Age to no one, birthday to friends')], help_text="Who can see user's age and birthday.", max_length=2)),
                ('web_site', models.URLField(blank=True, help_text="User's personal web site.")),
                ('interests', models.TextField(blank=True, help_text="User's interests separated by coma.")),
                ('kind_books', models.TextField(help_text="User's book subject preferences.")),
                ('about_me', models.TextField(help_text='A short review about user.')),
                ('active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'UserProfile',
            },
        ),
        migrations.CreateModel(
            name='Shelve',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Shelve's name.", max_length=150)),
                ('user', models.ForeignKey(help_text="Shelve' owner.", on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Shelve',
            },
        ),
        migrations.CreateModel(
            name='BookShelve',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Book')),
                ('shelve', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Shelve')),
            ],
            options={
                'db_table': 'BookShelve',
            },
        ),
    ]

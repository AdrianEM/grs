# Generated by Django 2.2.1 on 2019-05-29 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190528_2112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'ordering': ['created']},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender_view',
            field=models.CharField(choices=[('F', 'Friends only'), ('E', 'Everyone'), ('N', 'No one')], help_text="Who can see user's gender", max_length=2),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location_view',
            field=models.CharField(choices=[('F', 'Friends only'), ('E', 'Everyone'), ('N', 'No one')], help_text="Who can see user's location.", max_length=2),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='who_can_see_last_name',
            field=models.CharField(choices=[('F', 'Friends only'), ('E', 'Everyone'), ('N', 'No one')], max_length=2),
        ),
    ]
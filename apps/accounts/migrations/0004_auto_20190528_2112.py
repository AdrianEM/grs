# Generated by Django 2.2.1 on 2019-05-28 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20190528_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shelve',
            name='owner',
            field=models.ForeignKey(help_text="Shelve' owner.", on_delete=django.db.models.deletion.CASCADE, related_name='shelves', to='accounts.UserProfile'),
        ),
    ]

# Generated by Django 2.2.1 on 2019-06-13 19:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_readinggroup_creator'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReadinGroupUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('active', models.BooleanField(db_column='Active', default=False)),
                ('invitation_answered', models.BooleanField(default=False)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.ReadingGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.UserProfile')),
                ('who_invites', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='who_invites', to='accounts.UserProfile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

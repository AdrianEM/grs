# Generated by Django 2.2.1 on 2019-06-03 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20190602_2050'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_book', models.BooleanField(db_column='AddBook', default=True, help_text='Add a book to your shelves')),
                ('add_quote', models.BooleanField(db_column='AddQuote', default=True, help_text='Add a quote')),
                ('recommend_book', models.BooleanField(db_column='RecommendBook', default=True, help_text='Recommend a book')),
                ('add_new_status', models.BooleanField(db_column='AddNewStatus', default=True, help_text="Add a new status to a book you're reading")),
                ('comment_so_review', models.BooleanField(db_column='CommentSoReview', default=True, help_text="Comment on someone's review")),
                ('vote_book_review', models.BooleanField(db_column='VoteBookReview', default=True, help_text='Vote for a book review')),
                ('add_friend', models.BooleanField(db_column='AddFried', default=True, help_text='Add a friend')),
                ('comment_book_or_discussion', models.BooleanField(db_column='CommentBookOrDiscussion', default=True, help_text='Comment on a book or discussion')),
                ('join_group', models.BooleanField(db_column='JoinGroup', default=True, help_text='Join a group')),
                ('answer_poll', models.BooleanField(db_column='AnswerPoll', default=True, help_text='Answer a poll')),
                ('enter_giveaway', models.BooleanField(db_column='EnterGiveaway', default=True, help_text='Enter a Giveaway')),
                ('ask_answer', models.BooleanField(db_column='AskAnswer', default=True, help_text='Ask or answer a question')),
                ('follow_author', models.BooleanField(db_column='FollowAuthor', default=True, help_text='Follow an author')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.UserProfile')),
            ],
            options={
                'db_table': 'FeedSetting',
            },
        ),
    ]

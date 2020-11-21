from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from model_utils.models import TimeStampedModel

from goodreads.settings import GENDER, PERMISSION_VIEW, AGE_BIRTHDAY_PRIVACY, PROFILE_PERMISSIONS_VIEW, LANGUAGES, \
    EMAIL_FREQUENCY, COMMENT_NOTIFICATION, DISCUSSION_EMAIL_FREQUENCY, GROUP_GET_EMAIL_FREQUENCY, GROUP_TOPIC, \
    GROUP_PRIVACY


class Role(models.Model):
    READER = 1
    LIBRARIAN = 2
    STAFF = 3
    ADMIN = 4

    ROLE_CHOICES = (
        (READER, 'reader'),
        (LIBRARIAN, 'librarian'),
        (STAFF, 'staff'),
        (ADMIN, 'admin')
    )

    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()


class UserProfileManager(models.Manager):

    def get_email_settings(self, user_id):
        return EmailSettings.objects.get(user_id=user_id)

    def get_feed_settings(self, user_id):
        return FeedSetting.objects.get(user_id=user_id)

    def create_default_shelves(self, user_profile):
        from apps.books.models import Shelve
        default_shelves_name = ['read', 'to-read', 'currently-reading']
        for shelve_name in default_shelves_name:
            shelve = Shelve(name=shelve_name, owner=user_profile)
            shelve.save()

    def exist_email(self, email, user):
        return User.objects.filter(~models.Q(id=user.id), email=email).exists()


class UserProfile(AbstractUser, TimeStampedModel):
    full_name = models.CharField(max_length=150, db_column='FullName')
    email = models.EmailField(unique=True)
    birthday = models.DateField(db_column='Birthday', help_text=_('birthday'), blank=True, null=True)
    who_can_see_last_name = models.CharField(choices=PERMISSION_VIEW, max_length=2, default='F',
                                             db_column='WhoCanSeeLastName')
    photo = models.ImageField(help_text=_('profile_image'), db_column='Photo', blank=True)
    city = models.CharField(max_length=70, help_text=_('user_city'), blank=True, db_column='City')
    state = models.CharField(max_length=70, help_text=_('user_province'), db_column='State')
    country = CountryField(blank_label=_('select_country'), help_text=_('country'), db_column='Country')
    location_view = models.CharField(choices=PERMISSION_VIEW, help_text=_('who_user_location'), max_length=2,
                                     default='E', db_column='LocationView')
    gender = models.CharField(choices=GENDER, help_text=_('gender'), max_length=2, blank=True,
                              db_column='Gender')
    gender_view = models.CharField(choices=PERMISSION_VIEW, help_text=_('gender_view'), max_length=2,
                                   default='F', db_column='GenderView')
    age_view = models.CharField(choices=AGE_BIRTHDAY_PRIVACY, help_text=_('age_view'),
                                max_length=2, default='2', db_column='AgeView')
    web_site = models.URLField(help_text=_('web_site'), blank=True, db_column='WebSite')
    interests = models.TextField(help_text=_('interests'), blank=True, db_column='Interests')
    kind_books = models.TextField(help_text=_('book_subject_preferences'), blank=True, db_column='KindBooks')
    about_me = models.TextField(help_text=_('user_about_me'), blank=True, db_column='AboutMe')
    active = models.BooleanField(default=True, db_column='Active')
    roles = models.ManyToManyField(Role)

    objects = UserProfileManager()

    class Meta:
        db_table = 'UserProfile'
        ordering = ['created']

    def __str__(self):
        return self.full_name


class UserSettings(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    allow_non_friends_follow_reviews = models.BooleanField(default=True, db_column='AllowNonFriendsFollowReviews',
                                                           help_text=_('allow-nonfriends-to-comments-reviews'))
    who_can_send_me_private_msg = models.CharField(choices=PERMISSION_VIEW,
                                                   help_text=_('who_can_send_me_private_message'),
                                                   db_column='WhoCanSendMePrivMessages', max_length=2, default='F')
    email_visibility = models.CharField(choices=PERMISSION_VIEW, help_text=_('email_visibility'),
                                        db_column='EmailVisibility', max_length=2)
    challenge_question = models.TextField(help_text=_('challenge_question'), db_column='ChallengeQuestion',
                                          max_length=2)
    profile_view = models.CharField(choices=PROFILE_PERMISSIONS_VIEW, help_text=_('profile_view'),
                                    db_column='ProfileView', default='G', max_length=2)
    # Site customization
    recommendations = models.BooleanField(default=True, db_column='Recommendations', help_text=_('Recommendations'))
    language = models.CharField(choices=LANGUAGES, max_length=2, db_column='Language', help_text=_('Language'))

    class Meta:
        db_table = 'UserSettings'


class ReadingGroup(TimeStampedModel):
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reading_groups')
    name = models.CharField(max_length=150, db_column='Name', help_text=_('Name'))
    description = models.TextField(help_text=_('Description'), db_column='Description')
    rules = models.TextField(help_text=_('Rules'), db_column='Rules', blank=True)
    show_rules_only_new_members = models.BooleanField(default=True, help_text=_('Show rules only to new members'),
                                                      db_column='ShowRulesOnlyNewMembers')
    topic = models.CharField(choices=GROUP_TOPIC, max_length=3, help_text=_('Group or bookclub topic'),
                             db_column='Topic')
    subtopic = models.CharField(max_length=3, help_text=_('Subtopic'), db_column='subtopic', blank=True)
    tags = models.TextField(help_text=_('Tags'), db_column='Tags')
    privacy = models.CharField(choices=GROUP_PRIVACY, max_length=2, help_text=_('this group is'), default='PU',
                               db_column='Privacy')
    only_adults = models.BooleanField(default=False, help_text=_('For adults only'), db_column='OnlyAdults')
    non_mod_add_book = models.BooleanField(default=True,
                                           help_text=_('Non-moderator can add books to this group\'s shelf'),
                                           db_column='NonModeratorAddBook')
    non_mod_add_event = models.BooleanField(default=True, help_text=_('Non-moderator can add events'),
                                            db_column='NonModeratorAddEvent')
    mod_post_highlighted = models.BooleanField(default=True,
                                               help_text=_('Moderator posts are highlighted'),
                                               db_column='ModeratorPostHighlighted')
    meet_real_life = models.BooleanField(default=False, db_column='MeetRealLife',
                                         help_text=_('This group meets in real life'))
    display_video_top = models.BooleanField(default=False, db_column='DisplayVideo',
                                            help_text=_('Display videos at the top of this group\'s homepage'))
    challenge_question = models.TextField(blank=True, db_column='ChallengeQuestion',
                                          help_text=_('Challenge question, only for private groups'))
    postal_code = models.CharField(max_length=25, help_text=_('Postal code(for local group)'), db_column='PostalCode',
                                   blank=True)
    country = CountryField(blank_label=_('select_country'), help_text=_('country'), db_column='Country')
    active = models.BooleanField(default=True, db_column='Active')
    website = models.CharField(max_length=150, blank=True, db_column='WebSite', help_text=_('Affiliated website'))
    group_email_setting = models.CharField(choices=GROUP_GET_EMAIL_FREQUENCY, default='D', db_column='GroupEmailSett',
                                           help_text=_('Group discussion email settings'), max_length=2)


class EmailSettings(TimeStampedModel):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='email_setting')
    email_frequency = models.CharField(choices=EMAIL_FREQUENCY, db_column='EmailFrequency',
                                       help_text=_('Email Frequency'), max_length=2)
    include_top_friends_only = models.BooleanField(default=False, db_column='IncludeTopFriendsOnly',
                                                   help_text=_('Include top friends only'))
    include_to_read_books = models.BooleanField(default=True, db_column='IncludeToReadBooks',
                                                help_text=_('Include to read books'))
    # Event notifications
    likes_my_status = models.BooleanField(default=True, db_column='WhenSOLikeMyStatus',
                                          help_text=_('When someone like my update, review, note, highlight, photo, '
                                                      'quiz or writing'))
    sends_me_message = models.BooleanField(default=True, db_column='SendsMeMessage', help_text=_('Sends me a message'))
    adds_me_friend = models.BooleanField(default=True, db_column='AddMeAsFriend', help_text=_('Adds me as a friend'))
    follow_my_review = models.BooleanField(default=True, db_column='FollowMyReview', help_text=_('Follows my review'))
    invites_group = models.BooleanField(default=True, db_column='InviteGroup',
                                        help_text=_('Invites me to join a group'))
    invites_event = models.BooleanField(default=True, db_column='InviteEvent', help_text=_('Invites me to an event'))
    invites_trivia = models.BooleanField(default=True, db_column='InviteTrivia', help_text=_('Invites to play trivia'))
    ask_vote = models.BooleanField(default=True, db_column='AskVote',
                                   help_text=_('Asks me to vote on a Listopia list, take a quiz, or like a quote'))
    invites_poll = models.BooleanField(default=True, db_column='InvitePoll', help_text=_('Invites me to answer a poll'))
    mention_recommender = models.BooleanField(default=True, db_column='MentionsRecommender',
                                              help_text=_('Mentions me as a recommender'))
    recommend_book = models.BooleanField(default=True, db_column='RecommendBook',
                                         help_text=_('Recommends me a book'))
    # Comments and actions notification
    comment_review = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Comments on my book reviews'),
                                      db_column='CommentsReview', default='B', max_length=2)
    comment_profile = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Comments on my profile'),
                                       db_column='CommentProfile', default='B', max_length=2)
    like_listopia = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Likes my Listopia list'),
                                     db_column='LikeListopia', default='E', max_length=2)
    comment_listopia = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Comments on my Listopia list'),
                                        db_column='CommentListopia', default='B', max_length=2)
    comment_recommendation = models.CharField(choices=COMMENT_NOTIFICATION,
                                              help_text=_(
                                                  'Comments on a recommendation that I’ve given or commented on')
                                              , db_column='CommentRecommendation', default='B', max_length=2)
    comment_poll = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Comments on my poll'),
                                    db_column='CommentPoll', default='B', max_length=2)
    comment_trivia = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Comments on my trivia question'),
                                      db_column='CommentTrivia', default='B', max_length=2)
    comment_shelve = models.CharField(choices=COMMENT_NOTIFICATION,
                                      help_text=_('Comments on my shelvings, progress updates, notes, quotes,'
                                                  ' or highlights'), db_column='CommentShelve', default='B',
                                      max_length=2)
    comment_activity = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Comments on an activity or review I'
                                                                                  ' commented on'),
                                        db_column='CommentActivity', default='B', max_length=2)
    comment_qa = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Comments on a Goodreads Q&A that I’ve '
                                                                            'answered or commented on'),
                                  db_column='CommentQA', default='B', max_length=2)
    like_question = models.CharField(choices=COMMENT_NOTIFICATION, help_text=_('Likes my question or answer for '
                                                                               'Goodreads Q&A'),
                                     db_column='LikeQuestion', default='E', max_length=2)
    list_giveaway_book_toread = models.CharField(choices=COMMENT_NOTIFICATION, default='E', help_text=_('Lists a '
                                                                                                        'Giveaway with a book I added as To-Read'),
                                                 db_column='ListBookToRead',
                                                 max_length=2)
    list_giveaway_author_fallow = models.CharField(choices=COMMENT_NOTIFICATION, default='B',
                                                   help_text=_('Lists a Giveaway with a book by an author I follow'),
                                                   db_column='ListGiveAwayAuthorFollow', max_length=2)
    comment_friendship = models.CharField(choices=COMMENT_NOTIFICATION, default='B', help_text=_('Comments on my '
                                                                                                 'friendship with another user'),
                                          db_column='CommentFriendship',
                                          max_length=2)
    post_note = models.CharField(choices=COMMENT_NOTIFICATION, default='B',
                                 help_text=_('Posts notes and highlights for a book or author I have previously shelved'
                                             ' (friend/following/author/notable)'),
                                 db_column='PostNote', max_length=2)
    # Newsletter
    monthly_newsletter = models.BooleanField(default=True, help_text=_('monthly_goodreads_newsletters'),
                                             db_column='MonthlyNewsletter')
    newsletter_favorite_genre = models.BooleanField(default=True, help_text=_('newsletter_favorite_genre'),
                                                    db_column='NewsletterFavoriteGenre')
    young_newsletter = models.BooleanField(default=True, help_text=_('young_newsletter'), db_column='YoungNewsletter')
    romance_newsletter = models.BooleanField(default=True, help_text=_('romance_newsletter'),
                                             db_column='RomanceNewsletter')
    monthly_new_release = models.BooleanField(default=True, help_text=_('monthly_new_release'),
                                              db_column='MonthlyNewRelease')
    monthly_new_release_only_author_read = models.BooleanField(default=False,
                                                               db_column='MonthlyNewReleaseOnlyAuthorRead',
                                                               help_text=_('monthly_new_release_only_author_read'))
    new_features_gr = models.BooleanField(default=True, help_text=_('new_features_gr'), db_column='NewFeaturesGr')
    new_offers = models.BooleanField(default=False, help_text=_('new_offers'), db_column='NewOffers')
    books_authors_events = models.BooleanField(default=False, help_text=_('books_authors_events'),
                                               db_column='BooksAuthorsEvents')
    update_giveaway_won = models.BooleanField(default=True, help_text=_('update_giveaway_won'),
                                              db_column='UpdateGiveawayWon')
    update_giveaway_entered = models.BooleanField(default=True, help_text=_('update_giveaway_entered'),
                                                  db_column='UpdateGiveawayEntered')
    weekly_digest = models.BooleanField(default=True, help_text=_('weekly_digest'), db_column='WeeklyDigest')
    author_rated = models.BooleanField(default=True, help_text=_('author_rated'), db_column='AuthorRated')
    book_available = models.BooleanField(default=True, help_text=_('book_available'), db_column='BookAvailable')
    author_release = models.BooleanField(default=True, help_text=_('author_release'), db_column='AuthorRelease')
    recommendation_finish_book = models.BooleanField(default=True, help_text=_('recommendation_finish_book'),
                                                     db_column='RecommendationFinishBook')
    discussion_new_post = models.CharField(choices=DISCUSSION_EMAIL_FREQUENCY, default='D',
                                           help_text=_('discussion_new_post'), db_column='DiscussionNewPost',
                                           max_length=1)
    follow_discussion = models.BooleanField(default=True, help_text=_('follow_discussion'),
                                            db_column='FollowDiscussion')
    group_start_reading = models.BooleanField(default=True, help_text=_('group_start_reading'),
                                              db_column='GroupStartReading')

    class Meta:
        db_table = 'EmailSetting'


class ReadingGroupEmailSetting(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE)
    get_email = models.CharField(choices=GROUP_GET_EMAIL_FREQUENCY, default='N', max_length=1)


class FeedSetting(TimeStampedModel):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='feed_setting')
    # Book activity
    add_book = models.BooleanField(default=True, db_column='AddBook', help_text=_('Add a book to your shelves'))
    add_quote = models.BooleanField(default=True, db_column='AddQuote', help_text=_('Add a quote'))
    recommend_book = models.BooleanField(default=True, db_column='RecommendBook', help_text=_('Recommend a book'))
    add_new_status = models.BooleanField(default=True, db_column='AddNewStatus',
                                         help_text=_('Add a new status to a book you\'re reading'))
    # Reviews
    comment_so_review = models.BooleanField(default=True, db_column='CommentSoReview',
                                            help_text=_('Comment on someone\'s review'))
    vote_book_review = models.BooleanField(default=True, db_column='VoteBookReview',
                                           help_text=_('Vote for a book review'))
    # Only on Goodreads.com
    add_friend = models.BooleanField(default=True, db_column='AddFried', help_text=_('Add a friend'))
    comment_book_or_discussion = models.BooleanField(default=True, db_column='CommentBookOrDiscussion',
                                                     help_text=_('Comment on a book or discussion'))
    join_group = models.BooleanField(default=True, db_column='JoinGroup', help_text=_('Join a group'))
    answer_poll = models.BooleanField(default=True, db_column='AnswerPoll', help_text=_('Answer a poll'))
    enter_giveaway = models.BooleanField(default=True, db_column='EnterGiveaway', help_text=_('Enter a Giveaway'))
    ask_answer = models.BooleanField(default=True, db_column='AskAnswer', help_text=_('Ask or answer a question'))
    follow_author = models.BooleanField(default=True, db_column='FollowAuthor', help_text=_('Follow an author'))

    class Meta:
        db_table = 'FeedSetting'


class ReadingGroupUsers(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name='reading_group_users')
    active = models.BooleanField(default=False, db_column='Active')
    who_invites = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='+')
    invitation_answered = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


# Create the first reading group user which is the creator
@receiver(post_save, sender=ReadingGroup)
def create_group(sender, instance, **kwargs):
    if kwargs.get('created', False):
        reading_group_user = ReadingGroupUsers(user=instance.creator, group=instance, active=True,
                                               who_invites=instance.creator, invitation_answered=True)
        reading_group_user.save()
        group_email_setting = ReadingGroupEmailSetting(user=instance.creator, group=instance)
        group_email_setting.save()


@receiver(post_save, sender=UserProfile)
def create_default_user_settings(sender, instance, **kwargs):
    if kwargs.get('created', False):
        email_setting = EmailSettings(user=instance)
        email_setting.save()
        feed_setting = FeedSetting(user=instance)
        feed_setting.save()


from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import settings
import os.path
import uuid
import datetime

POST_TYPE_GENERAL = 1
POST_TYPE_REPORT = 2
POST_TYPES = [
    (POST_TYPE_GENERAL, 'General'),
    (POST_TYPE_REPORT, 'Report'),
]


def user_dir(instance, filename):
    return 'static/avatars/{0}/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', related_name='profile', null=False, primary_key=True)
    # avatar = models.ImageField(upload_to=user_dir, default='/static/avatars/default.jpg')
    avatar = models.CharField(max_length=1024, null=True, blank=True)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)
    score = models.IntegerField(default=0)
    # TODO:
    # image, current equipment, following spots, total votes, badges, instructor

    def profile_pic(self):
        default_avatar_url = '/static/avatars/default.jpg'
        return self.avatar if self.avatar else default_avatar_url

    def unique_image_path(self):
        random_filename = "{}.jpg".format(str(uuid.uuid4())[:8])
        file_path = "{}/donkidik/static/avatars/{}/{}".format(settings.BASE_DIR, self.user.id, random_filename)
        if os.path.isfile(file_path):
            return unique_image_path()
        return file_path

    def upvote(self):
        print "got an upvote request, score is %s" % self.score
        self.score += 1
        self.save()
        print "now its %s" % self.score
        return

    def downvote(self):
        self.score = max(self.score - 1, 0)
        self.save()
        return

    def jsonify(self):
        userJson = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'username': self.user.username,
            'score': self.score,
            'follows': [u.pk for u in self.follows.all()],
            'followed_by': [u.pk for u in self.followed_by.all()],
            'avatar': self.avatar
        }
        return userJson

    def __str__(self):
        return '<%s - UserProfile>' % self.user.first_name

@receiver(post_save, sender='auth.User')
def create_profile(sender, **kwargs):
    # make sure its not an update
    if kwargs.get('created', False):
        UserProfile.objects.get_or_create(user=kwargs.get('instance'))
    return

class Post(models.Model):
    author = models.ForeignKey('auth.User', related_name='posts')
    #post_type = models.ForeignKey('PostType')
    post_type = models.IntegerField(choices=POST_TYPES, default=POST_TYPE_GENERAL, blank=False, null=False, db_index=True)
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    upvotes = models.ManyToManyField('auth.User', related_name='upvoted_posts')
    downvotes = models.ManyToManyField('auth.User', related_name='downvoted_posts')
    score = models.IntegerField(default=0)
    # TODO: add image, video

    def jsonify(self, user=None):
        ret = {     'post_type':self.post_type,
                    'author': { 'name': self.author.first_name,
                                'id': self.author.id,
                                'score': self.author.profile.score,
                                'avatar': self.author.profile.avatar
                                },
                    'text': self.text,
                    'date': [ self.date.day,self.date.month,self.date.year],
                    'time': [ self.date.hour,self.date.minute,self.date.second],
                    'seconds_passed': int((datetime.datetime.utcnow().replace(tzinfo=timezone.utc) - self.date).total_seconds()),
                    'comments': [ c.jsonify() for c in self.comments.all() ],
                    'score':self.score,
                    'post_id':self.pk,
                    'upvotes':[ u.pk for u in self.upvotes.all() ],
                    'downvotes':[ u.pk for u in self.downvotes.all() ]
                }

        if user:
            if user.id == self.author.id:
                ret['is_owner'] = True
            if user.id in ret['upvotes']:
                ret['is_upvoted'] = True;
            if user.id in ret['downvotes']:
                ret['is_downvoted'] = True;

        if hasattr(self,'meta'):
            # there is a meta record for this post
            ret.update({    'knots': self.meta.knots,
                            'gust': self.meta.gust,
                            'spot': self.meta.spot.name if hasattr(self.meta, 'spot') and self.meta.spot else None,
                            'spot_id': self.meta.spot.pk if hasattr(self.meta, 'spot') and self.meta.spot else None,
                            'action_date': self.meta.date
                        })
        return ret

    def upvote(self, voting_user):
        print "Voting user: %s" %voting_user.pk
        adjust_score = 0
        if self.upvotes.filter(pk = voting_user.pk):
            self.upvotes.remove(voting_user)
            self.score -= 1
            self.author.profile.downvote()
            return -1
        if self.downvotes.filter(pk = voting_user.pk):
            self.downvotes.remove(voting_user)
            self.score+=1
            self.author.profile.upvote()
            adjust_score = 1
        self.upvotes.add(voting_user)
        self.score+=1
        self.author.profile.upvote()
        return 1+adjust_score

    def downvote(self, voting_user):
        adjust_score = 0
        if self.downvotes.filter(pk = voting_user.pk):
            self.downvotes.remove(voting_user)
            self.score+=1
            self.author.profile.upvote()
            return 1
        if self.upvotes.filter(pk = voting_user.pk):
            self.upvotes.remove(voting_user)
            self.score -= 1
            self.author.profile.downvote()
            adjust_score = -1
        self.downvotes.add(voting_user)
        self.score -= 1
        self.author.profile.downvote()
        return -1 + adjust_score

    def __str__(self):
        post_type = 'General' if self.post_type == POST_TYPE_GENERAL else 'Report'
        return '%s (%s)' % (post_type, self.author)

class PostType(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return "< PostType: %s >" %self.name

class PostMeta(models.Model):
    post = models.OneToOneField('Post', related_name='meta', primary_key=True)
    knots = models.IntegerField(blank=True, null=True)
    gust = models.IntegerField(blank=True, null=True)
    spot = models.ForeignKey('Spot', related_name='posts_metas',blank=True,null=True)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return "< PostMeta for post %s>" %self.post.id 

class Comment(models.Model):
    post = models.ForeignKey('Post', related_name='comments', blank=True, null=True)
    user = models.ForeignKey('auth.User',related_name='comments')
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    # TODO
    # votes
    def jsonify(self):
        comment = {
                    'text': self.text,
                    'date': [self.date.day,self.date.month,self.date.year],
                    'time': [self.date.hour,self.date.minute,self.date.second],
                    'user': self.user.first_name,
                    'user_id': self.user.pk,
                    'comment_id': self.pk,
                    }
        return comment

    def __str__(self):
        return "< Comment by %s: %s >" %(self.user.first_name, self.text)

class Spot(models.Model):
    name = models.CharField(max_length=50, unique=True)
    #location
    #country

    def jsonify(self):
        spot = {
                    'name': self.name
                }
        return spot

    def __str__(self):
        return "< Spot: %s >" %self.name

class Session(models.Model):
    spot = models.ForeignKey('Spot')
    date = models.DateTimeField()
    owner = models.ForeignKey('auth.User', related_name='own_sessions')
    users = models.ManyToManyField('auth.User', related_name='attending_sessions')
    private = models.BooleanField(default=False)
    
    def jsonify(self):
        session = {
                    'users': [ u.profile.jsonify() for u in self.users ],
                    'date': [self.date.day,self.date.month,self.date.year],
                    'time': [self.date.hour,self.date.minute,self.date.second],
                    'spot': self.spot.name
                                                                                }
        return session

    def __str__(self):
        return "< Session: %s at %s >" %(self.date, self.spot.name)
    
class Forecast(models.Model):
    user = models.ForeignKey('auth.User')
    date = models.DateTimeField(default=timezone.now) # date forecast was made
    f_date = models.DateTimeField() # forecast date
    knots = models.IntegerField()
    gust = models.IntegerField(null=True)
    spots = models.ManyToManyField('Spot',related_name='forecasts')
    sessions = models.ManyToManyField('Session', related_name='forecasts')
    text = models.TextField()

    def jsonify(self):
        forecast = {
                    'user': self.user.username,
                    'user_id': self.user.id,
                    'date': [self.date.day,self.date.month,self.date.year],
                    'time': [self.date.hour,self.date.minute,self.date.second],
                    'f_date': [self.date.day,self.date.month,self.date.year],
                    'f_time': [self.date.hour,self.date.minute,self.date.second],
                    'spots': [ s.jsonify() for s in spots ]
        }
        return session
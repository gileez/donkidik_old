from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User',related_name='profile', primary_key=True)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)
    score = models.IntegerField(default=0)
    # TODO:
    # image, current equipment, following spots, total votes, badges, instructor

    def upvote(self):
        self.score += 1
        return

    def downvote(self):
        self.score = max(self.score - 1, 0)
        return

    def jsonify(self):
        userJson = {
                        'first_name': self.user.first_name,
                        'email': self.user.email,
                        'username': self.user.username,
                        'score': self.score,
                        # TODO : picture
                                                            }
        return userJson

    def __str__(self):
        return '<%s - UserProfile>' %self.user.first_name

class Post(models.Model):
    author = models.ForeignKey('auth.User', related_name='posts')
    post_type = models.ForeignKey('PostType')
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    votes = models.ManyToManyField('auth.User', related_name='voted_posts')
    score = models.IntegerField(default=0)
    # TODO: add image, video

    def jsonify(self):
        ret = {     'post_type':self.post_type.name,
                    'type_id': self.post_type.id,
                    'author': { 'name': self.author.first_name,
                                'id': self.author.id
                                },
                    'text': self.text,
                    'date': [ self.date.day,self.date.month,self.date.year],
                    'time': [ self.date.hour,self.date.minute,self.date.second],
                    'comments': [ c.jsonify() for c in self.comments ],
                    'score':self.score,
                }
        if hasattr(self,'meta'):
            # there is a meta record for this post
            ret.update({    'knots': self.meta.knots,
                            'gust': self.meta.gust,
                            'spot': self.meta.spot.name if hasattr(self.meta, 'spot') and self.meta.spot else None,
                            'action_date': self.meta.date
                        })
        return ret

    def upvote(self, voting_user):
        self.votes.add(voting_user)
        self.score+=1
        self.user.profile.upvote()
        return True

    def downvote(self, voting_user):
        self.votes.remove(voting_user)
        self.score = self.score - 1 if self.score > 0 else 0
        self.user.profile.downvote()
        return True

    def __str__(self):
        return '<%s> %s' %(self.post_type.name, self.author.username)

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
                    'user': self.user,
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
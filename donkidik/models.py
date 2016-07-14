from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User',related_name='profile', primary_key=True)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)
    def __str__(self):
        return '<%s - UserProfile>' %self.user.first_name

class Post(models.Model):
    author = models.ForeignKey('auth.User', related_name='posts')
    post_type = models.ForeignKey('PostType')
    text = models.TextField()
    published_date = models.DateTimeField(blank=True, null=True)
    # TODO: add image, video

    def publish(self):
        self.published_date = timezone.now()
        self.save()

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
    spot = models.ForeignKey('Spot', related_name='posts_meta',blank=True,null=True)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return "< PostMeta for post %s>" %self.base_post.id 

class Spot(models.Model):
    name = models.CharField(max_length=50)
    #location
    #country
    def __str__(self):
        return "< Spot: %s >" %self.name

class Session(models.Model):
    spot = models.ForeignKey('Spot')
    date = models.DateTimeField()
    users = models.ManyToManyField('auth.User', related_name='attending_sessions')

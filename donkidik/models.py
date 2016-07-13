from django.db import models
from django.utils import timezone
from annoying.fields import AutoOneToOneField

class Follow(models.Model):
    follower = models.ForeignKey('auth.User')
    followed = models.ForeignKey('auth.User')
    def __str__(self):
        return '%s follows %s' %(self.follower.first_name, self.followed.first_name)    

class PostType(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey('auth.User')
    post_type = models.ForeignKey(PostType)
    text = models.TextField()
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return '<%s> %s' %(self.post_type.name, self.author.username)


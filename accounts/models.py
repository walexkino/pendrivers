from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
import cloudinary
from cloudinary.models import CloudinaryField
from django.utils.safestring import mark_safe

# Create your models here.

class Subscribe(models.Model):
    email_id = models.EmailField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email_id

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    title = models.CharField(max_length=120, default="My Title")
    picture = models.ImageField(upload_to='profile_images', blank=True)
    # picture = CloudinaryField('image')
    social_media = models.CharField(max_length=120, default="")
    bio = models.TextField(default='', blank=True)
    money = models.IntegerField(default=0)
    account_number = models.CharField(max_length=10, default='0')
    expert_badge = models.BooleanField(default=False)
    password_code = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    city = models.CharField(max_length=100, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    organization = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.user.username

class Followers(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='myfollowers')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amfollowing')

    def __str__(self):
        return '%s following %s' % (self.follower, self.following)
    




def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = UserProfile(user=user)
        user_profile.save()
post_save.connect(create_profile, sender=User)

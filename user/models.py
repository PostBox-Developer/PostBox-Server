from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


class User(AbstractUser):
    user_id = models.CharField(unique=True, max_length=20)     # id
    username = models.CharField(unique=False, max_length=20)    # user name (본명)
    root_folder = models.OneToOneField("storage.Folder", on_delete=models.PROTECT, related_name='User')

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return self.user_id


class UserFollowing(models.Model):
    follower = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='userFollowing_follower')
    followee = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='userFollowing_followee')
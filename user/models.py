from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework import exceptions


# def user_id(value):
#     if len(value) < 6:
#         raise exceptions.ParseError("User_id is too short.")

class User(AbstractUser):
    user_id = models.CharField(unique=True, max_length=20) #, validators=[user_id])     # id
    username = models.CharField(unique=False, max_length=20)    # user name (본명)
    root_folder = models.OneToOneField("storage.Folder", on_delete=models.CASCADE, related_name='user', null=True)      # on_delete=models.PROTECT에서 변경
    profile_image_url = models.CharField(default="https://postbox-public-image.s3.ap-northeast-2.amazonaws.com/user_profile/default.png", max_length=200)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return self.user_id

class UserFollowing(models.Model):
    follower = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='userFollowing_follower')
    followee = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='userFollowing_followee')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followee"],
                name="userFollowing unique combination",
            ),
        ]
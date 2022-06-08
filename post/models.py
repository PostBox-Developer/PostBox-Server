from django.db import models
from django.utils import timezone
# from user.models import User
# from storage.models import File


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='post')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("post.Category", on_delete=models.SET_NULL, null=True, related_name="post")

class PostImage(models.Model):
    post = models.ForeignKey("post.Post", on_delete=models.CASCADE, related_name="postImage")
    s3_key = models.CharField(max_length=200)

class Category(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="category")
    name = models.CharField(max_length=20)

class PostAttachFile(models.Model):
    post = models.ForeignKey("post.Post", on_delete=models.CASCADE, related_name='postAttachFile')
    file = models.ForeignKey("storage.File", on_delete=models.CASCADE, related_name='postAttachFile')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "file"],
                name="postAttachFile unique combination",
            ),
        ]
        
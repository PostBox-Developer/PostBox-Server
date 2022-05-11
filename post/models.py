from django.db import models
from django.utils import timezone
# from user.models import User
# from storage.models import File


class Post(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    author = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='Post')
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    def modified(self):
        self.modified_at = timezone.now()
        self.save()


class PostAttachFile(models.Model):
    post = models.ForeignKey("post.Post", on_delete=models.CASCADE, related_name='PostAttachFile')
    file = models.ForeignKey("storage.File", on_delete=models.CASCADE, related_name='PostAttachFile')
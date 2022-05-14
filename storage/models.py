from django.db import models
from django.utils import timezone
# from user.models import User


class Folder(models.Model):
    PRIVATE_OF_Folder = (
        (0, '전체 공개'),
        (1, '친구 공개'),
        (2, '나만 보기'),
    )

    foldername = models.CharField(max_length=100)
    is_shared = models.BooleanField(default=False)
    is_public = models.IntegerField(choices=PRIVATE_OF_Folder, default=0)
    parent_folder = models.ForeignKey("self", on_delete=models.CASCADE, related_name='child_folder', null=True)        # 상위폴더 (하위폴더 필드는 필요X)
    creater = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='created_folder')                 # 생성자
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.foldername

    def modified(self):
        self.modified_at = timezone.now()
        self.save()


class File(models.Model):
    filename = models.CharField(max_length=100)
    uploader = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='uploaded_file')        # 생성자
    parent_folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='child_file')        # 상위폴더
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.filename

    def modified(self):
        self.modified_at = timezone.now()
        self.save()


class FolderSharing(models.Model):
    sharer = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='FolderSharing')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='FolderSharing')
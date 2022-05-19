from django.contrib import admin
from .models import Post, PostAttachFile

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']
    list_display_links = ['title', 'author']

@admin.register(PostAttachFile)
class PostAttachFileAdmin(admin.ModelAdmin):
    list_display = ['post', 'file']
    list_display_links = ['post', 'file']
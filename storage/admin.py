from django.contrib import admin
from .models import File, Folder

# Register your models here.
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['foldername', 'creater']
    list_display_links = ['foldername', 'creater']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploader']
    list_display_links = ['filename', 'uploader']
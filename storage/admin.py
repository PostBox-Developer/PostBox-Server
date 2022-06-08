from django.contrib import admin
from .models import File, Folder, FolderSharing

# Register your models here.
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['foldername', 'creater']
    list_display_links = ['foldername', 'creater']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploader']
    list_display_links = ['filename', 'uploader']

@admin.register(FolderSharing)
class FileAdmin(admin.ModelAdmin):
    list_display = ['folder', 'sharer']
    list_display_links = ['folder', 'sharer']
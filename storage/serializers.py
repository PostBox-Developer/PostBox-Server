from .models import File, Folder
from rest_framework import serializers

class FileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "id",
            "filename",
            "uploader_id",          # User의 user_id
            "uploader_name",        # User의 username
            "parent_folder_id",     # Folder의 id(PK)
            "created_at",
            "modified_at",
        ]

    uploader_id = serializers.SerializerMethodField("getUploaderId")
    uploader_name = serializers.SerializerMethodField("getUploaderName")
    parent_folder_id = serializers.SerializerMethodField("getParentFolderId")

    def getUploaderId(self, obj):
        return obj.uploader.user_id

    def getUploaderName(self, obj):
        return obj.uploader.username

    def getParentFolderId(self, obj):
        return obj.parent_folder.id

class FolderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = [
            "id",
            "foldername",
            "is_shared",
            "is_public",
            "parent_folder_id", # Folder의 id(PK)
            "creater_id",       # User의 user_id
            "creater_name",     # User의 username
            "created_at",
            "modified_at",      
        ]
    
    creater_id = serializers.SerializerMethodField("getCreaterId")
    creater_name = serializers.SerializerMethodField("getCreaterName")
    parent_folder_id = serializers.SerializerMethodField("getParentFolderId")

    def getCreaterId(self, obj):
        return obj.creater.user_id

    def getCreaterName(self, obj):
        return obj.creater.username

    def getParentFolderId(self, obj):
        if obj.parent_folder == None:
            return "null"
        else:
            return obj.parent_folder.id

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [

        ]
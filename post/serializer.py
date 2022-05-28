from django.forms import IntegerField
from .models import Post, PostAttachFile, Category
# user.serializer import userserializer
from rest_framework import serializers
from storage.models import File
import json
from django.core.serializers import serialize

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "desc",
            "author_id",    #   User의 user_id
            "author_name",  #   User의 username
            "created_at",
            "modified_at",
        ]

    author_id = serializers.SerializerMethodField("getAuthorId")
    author_name = serializers.SerializerMethodField("getAuthorName")

    def getAuthorId(self, obj):
        return obj.author.user_id

    def getAuthorName(self, obj):
        return obj.author.username


class PostAttachFileSerializer(serializers.ModelSerializer):
    # postAttachFile = serializers.PrimaryKeyRelatedField(queryset=PostAttachFile.objects.all())

    class Meta:
        model = PostAttachFile
        fields = [
            'post',
            'file',
            'postAttachFile_pk',
            #'post_',
            # 'postAttachFile',
            # 'file_',
        ]

    postAttachFile_pk = serializers.SerializerMethodField("getPostAttachFile_pk")

    def getPostAttachFile_pk(self,obj):
        return obj.pk

    # post_ = serializers.SerializerMethodField("getPost_")
    # file_ = serializers.SerializerMethodField("getFile_")

    # def getPost_(self, obj):
    #     # post = serialize('json', [obj.post,])   # 문자열
    #     # post_python_obj = json.loads(post)      # json 문자열에 대한 python 객체 list
    #     # post_json = json.dumps(post_python_obj[0])
    #     # return post_json
    #     return PostSerializer(obj.post).data

    # def getFile_(self, obj):
    #     return FileSerializer(obj.file).data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['pk', 'name']
    
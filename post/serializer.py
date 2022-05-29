from dataclasses import fields
from django.forms import IntegerField
from .models import Post, PostAttachFile, Category, PostImage
# user.serializer import userserializer
from rest_framework import serializers
from storage.models import File
import json
from django.core.serializers import serialize
from .image_bucket_config import secrets

class PostSerializer(serializers.ModelSerializer):
    author_id = serializers.ReadOnlyField(source='author.user_id')
    author_name = serializers.ReadOnlyField(source='author.username')
    image_list = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'pk', 'title', 'text', 'author_id', 'author_name',
            'category', 'created_at', 'modified_at', 'image_list',
        ]

    def get_image_list(self, instance):
        temp = PostImageSerializer(instance.postImage, many=True)
        return temp.data

class PostImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ['pk', 'url']

    def get_url(self, instance):
        return ('https://' + secrets['BUCKET_NAME']
                + '.s3.' + secrets['AWS_DEFAULT_REGION']
                + '.amazonaws.com/' + instance.s3_key)
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
    
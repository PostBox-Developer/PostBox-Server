from django.utils import timezone
from .models import Post, PostAttachFile, Category, PostImage
from .serializer import PostSerializer, PostAttachFileSerializer, CategorySerializer, PostImageSerializer, PostListSerializer
from .permissions import IsAuthorOfPost, IsOwnerOfPostImage, IsOwnerOfCategory
from user.models import User
from rest_framework import generics, status, exceptions
from rest_framework.authentication import TokenAuthentication# import permission
from storage.models import File
from user.models import User
from rest_framework.response import Response
from django.core.serializers import json as JSON
import json
from django.core import serializers
from rest_framework import permissions
import boto3
from .image_bucket_config import secrets

'''GET'''
class PostListAPI(generics.ListAPIView):
    serializer_class = PostListSerializer

    def get_queryset(self):
        try:
            user = User.objects.get(user_id=self.request.data['user_id'])
        except User.DoesNotExist:
            raise exceptions.ParseError('User dose not exist')

        if self.request.data['category_name'] in ['', None]:
            return Post.objects.filter(author=user)

        try:
            category = Category.objects.get(user=user, name=self.request.data['category_name'])
        except Category.DoesNotExist:
            raise exceptions.ParseError('Category dose not exist')

        return Post.objects.filter(author=user, category=category)

'''POST'''
class PostCreateAPI(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        if self.request.data['category_name'] in ['', None]:
            category = None
        else:
            try:
                category = Category.objects.get(user=self.request.user,
                                                name=self.request.data['category_name'])
            except Category.DoesNotExist:
                raise exceptions.ParseError('Category dose not exist')
        post = serializer.save(author=self.request.user, category=category)
        s3 = boto3.resource(
            's3',
            aws_access_key_id = secrets['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key = secrets['AWS_SECRET_ACCESS_KEY'],
            region_name = secrets['AWS_DEFAULT_REGION']
        )
        bucket = s3.Bucket(secrets['BUCKET_NAME'])
        for key in self.request.FILES:
            file = self.request.FILES[key]
            s3_key = str(post.pk) + '/' + str(hash(key + file.name + str(timezone.now())) & 0xffffffff)
            bucket.upload_fileobj(file, s3_key)
            PostImage.objects.create(post=post, s3_key=s3_key)

# ''' GET, PUT, DELETE '''
# class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     authentication_classes = [TokenAuthentication]

class PostImageDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfPostImage]
    authentication_classes = [TokenAuthentication]

class PostDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOfPost]
    authentication_classes = [TokenAuthentication]

'''GET'''
class CatecoryListAPI(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        user = User.objects.get(user_id=self.request.data['user_id'])
        return Category.objects.filter(user=user)

'''POST'''
class CatecoryCreateAPI(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

'''PUT'''
class CatecoryRenameAPI(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfCategory]
    authentication_classes = [TokenAuthentication]

'''DELETE'''
class CatecoryDeleteAPI(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfCategory]
    authentication_classes = [TokenAuthentication]

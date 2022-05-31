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
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


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


class PostCreateUpdateBase:
    def perform_create_or_update(self, serializer):
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


'''POST'''
class PostCreateAPI(generics.CreateAPIView, PostCreateUpdateBase):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        self.perform_create_or_update(serializer)


'''PUT'''
class PostUpdateAPI(generics.UpdateAPIView, PostCreateUpdateBase):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOfPost]
    authentication_classes = [TokenAuthentication]

    def perform_update(self, serializer):
        self.perform_create_or_update(serializer)


@api_view(['GET'])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    post_serializer = PostSerializer(post)
    response_post = post_serializer.data

    # response로 줄 PostAttachFile 내용 필터링
    post_attach_file_list = PostAttachFile.objects.filter(post=post)
    response_file_list = []
    for post_attach_file in post_attach_file_list:
        file = post_attach_file.file

        # path 찾기
        file_path = file.parent_folder.foldername + file.filename
        parent_folder = file.parent_folder
        while parent_folder.parent_folder != None:
            file_path = parent_folder.parent_folder.foldername + file_path
            parent_folder = parent_folder.parent_folder

        response_file_list.append({'pk':file.pk, 'path':file_path})

    return JsonResponse({
        'post': response_post,
        'attached_file_list': response_file_list
        }, json_dumps_params = {'ensure_ascii': False})


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


# 추후 권한 확인 추가
@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
@authentication_classes((TokenAuthentication, ))
def post_attach_file(request, pk):
    post = get_object_or_404(Post, pk=pk)
    detach_file_list = request.data.get('detach_file_list')
    attach_file_list = request.data.get('attach_file_list')

    # detach_file_list로 주어진 값이 없으면 pass, 있으면 처리
    if detach_file_list != '':
        detach_file_list = json.loads(detach_file_list)             # json 파싱

        for file_pk in detach_file_list:
            file = get_object_or_404(File, pk=file_pk)
            post_attach_file = get_object_or_404(PostAttachFile, post=post, file=file)
            post_attach_file.delete()

    # attach_file_list로 주어진 값이 있으면 처리
    if attach_file_list != '':
        attach_file_list = json.loads(attach_file_list)             # json 파싱
    
        for file_pk in attach_file_list:
            file = get_object_or_404(File, pk=file_pk)
            PostAttachFile.objects.create(post=post, file=file)

    # response로 줄 PostAttachFile 내용 필터링해서 제공하기
    post_attach_file_list = PostAttachFile.objects.filter(post=post)
    response_file_list = []
    for post_attach_file in post_attach_file_list:
        file = post_attach_file.file

        # path 찾기
        file_path = file.parent_folder.foldername + file.filename
        parent_folder = file.parent_folder
        while parent_folder.parent_folder != None:
            file_path = parent_folder.parent_folder.foldername + file_path
            parent_folder = parent_folder.parent_folder

        response_file_list.append({'pk':file.pk, 'path':file_path})

    return JsonResponse({
        "attached_file_list": response_file_list
        }, json_dumps_params = {'ensure_ascii': False})


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

from .models import Post, PostAttachFile, Category
from .serializer import PostSerializer, PostAttachFileSerializer, CategorySerializer
from user.models import User
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication# import permission
from storage.models import File
from user.models import User, user_id
from rest_framework.response import Response
from django.core.serializers import json as JSON
import json
from django.core import serializers
from rest_framework import permissions

''' GET, POST '''
class PostAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = []

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

''' GET, PUT, DELETE '''
class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = []

class PostAttachFileCreateAPI(generics.CreateAPIView):
    queryset = PostAttachFile.objects.all()
    serializer_class = PostAttachFileSerializer
    authentication_classes = [TokenAuthentication]

class PostAttachFileDeleteAPI(generics.DestroyAPIView):
    queryset = PostAttachFile.objects.all()
    serializer_class = PostAttachFileSerializer
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
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

'''DELETE'''
class CatecoryDeleteAPI(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

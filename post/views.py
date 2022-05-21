from .models import Post, PostAttachFile
from .serializer import PostSerializer, PostAttachFileSerializer
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication# import permission
from storage.models import File
from user.models import User
from rest_framework.response import Response
from django.core.serializers import json as JSON
import json
from django.core import serializers

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
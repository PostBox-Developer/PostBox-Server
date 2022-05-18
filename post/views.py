#from django.shortcuts import render

from .models import Post
from .serializer import PostSerializer
from rest_framework import generics

from user.models import User

class PostAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        author_id = self.request.data.get("author_id")

        userInstance = User.objects.get(user_id=author_id)

        serializer.save(author=userInstance)
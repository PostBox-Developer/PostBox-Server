from .models import Post
from .serializer import PostSerializer
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication# import permission

from user.models import User

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
from .models import Post
from .serializer import PostSerializer
from rest_framework import generics
# import TokenAutehtication
# import permission

from user.models import User

''' GET, POST '''
class PostAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = []

    def perform_create(self, serializer):
        # author_id = self.request.data.get("author_id")
        # userInstance = User.objects.get(user_id=author_id)
        # serializer.save(author=userInstance)

        serializer.save(author=self.request.user)

''' GET, PUT, DELETE '''
class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = []
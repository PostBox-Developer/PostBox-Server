from .models import File, Folder
from .serializers import *
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication

class FileAPIView(generics.ListCreateAPIView):
    
    serializer_class = FileListSerializer
    model = serializer_class.Meta.model
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        parent_folder = Folder.objects.get(id=self.request.data.get("parent_folder_id"))
        serializer.save(uploader = self.request.user, 
                        parent_folder = parent_folder)

    def get_queryset(self):
        parent_folder_id = self.request.data.get("parent_folder_id")

        if parent_folder_id == "null":
            queryset = self.model.objects.filter(
                uploader = self.request.user,
                parent_folder__isnull=True
            )
        else:
            queryset = self.model.objects.filter(
                uploader = self.request.user,
                parent_folder = parent_folder_id
            )

        return queryset

class FolderAPIView(generics.ListCreateAPIView):
    
    serializer_class = FolderListSerializer
    model = serializer_class.Meta.model
    authentication_classes = [TokenAuthentication]
    
    def perform_create(self, serializer):
        parent_folder_id = self.request.data.get("parent_folder_id")
        print(parent_folder_id)
        if parent_folder_id == "null":
            serializer.save(creater = self.request.user)
        else:
            parent_folder = Folder.objects.get(id=parent_folder_id)
            print(parent_folder)
            serializer.save(creater = self.request.user,
                            parent_folder = parent_folder)

    def get_queryset(self):
        parent_folder_id = self.request.data.get("parent_folder_id")

        if parent_folder_id == "null":
            queryset = self.model.objects.filter(
                creater = self.request.user,
                parent_folder__isnull=True
            )
        else:
            queryset = self.model.objects.filter(
                creater = self.request.user,
                parent_folder = parent_folder_id
            )

        return queryset
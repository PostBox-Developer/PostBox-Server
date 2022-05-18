from .models import File, Folder
from .serializers import *
from rest_framework import generics

class FileAPIView(generics.ListAPIView):
    
    serializer_class = FileListSerializer
    model = serializer_class.Meta.model
    
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

class FolderAPIView(generics.ListAPIView):
    
    serializer_class = FolderListSerializer
    model = serializer_class.Meta.model

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
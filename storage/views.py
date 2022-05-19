from .models import File, Folder
from .serializers import *
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes

import boto3
from .boto3_config import secrets

client = boto3.client('s3',
                        aws_access_key_id = secrets.get("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key = secrets.get("AWS_SECRET_ACCESS_KEY"),
                        region_name = secrets.get("AWS_DEFAULT_REGION"))

class FileListCreateAPIView(generics.ListCreateAPIView):
    
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

class FolderListCreateAPIView(generics.ListCreateAPIView):
    
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

@api_view(['DELETE'])
@authentication_classes((TokenAuthentication, ))
def delete_file(request):
    user = request.user

    ## request에서 받아야 할 것
    # file의 PK
    # file이 있는 경로
    file_id = request.data.get("file_id")
    file_path = request.data.get("file_path")   
    ## 나중에 디렉토리 구조 정하면.. 프론트에서 경로 정보 유지하다가 넘겨줄 것 염두에 둠.

    filterFile = File.objects.filter(
        uploader = user,
        id = file_id
    )
    
    # S3의 객체 삭제
    #### s3 버킷에서 사용자아이디+파일명 키 담아서 객체 삭제..
    s3_object_key = user.user_id + "/" + filterFile[0].filename
    s3_response = client.delete_object(Bucket="postbox-practice-1", Key=s3_object_key)
    
    # DB의 레코드 삭제
    filterFile.delete()
    
    return Response({"message": "success"}, status=status.HTTP_200_OK)
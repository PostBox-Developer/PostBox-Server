from pydoc import cli
from .models import File, Folder
from .serializers import *
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.http import JsonResponse
from django.utils import timezone

import boto3
from .boto3_config import secrets

client = boto3.client('s3',
                        aws_access_key_id = secrets.get("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key = secrets.get("AWS_SECRET_ACCESS_KEY"),
                        region_name = secrets.get("AWS_DEFAULT_REGION"))

resource = boto3.resource('s3',
                        aws_access_key_id = secrets.get("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key = secrets.get("AWS_SECRET_ACCESS_KEY"),
                        region_name = secrets.get("AWS_DEFAULT_REGION"))

BucketName = secrets.get("BUCKET_NAME")

'''
홈 디렉토리 폴더-파일 목록 조회
GET: storage/get_home_folder/
'''
@api_view(['GET'])
@authentication_classes((TokenAuthentication, ))
def get_home_folder(request):
    login_user = request.user

    # 루트 폴더 조회 
    rootFolder = Folder.objects.filter(
        creater = login_user,           # creater가 로그인된 유저이고
        parent_folder__isnull=True      # parent_folder가 null인 것
    )[0]

    # parent_folder가 rootFolder인 폴더와 파일들 조회
    folders = Folder.objects.filter(
        creater = login_user,
        parent_folder = rootFolder
    )

    files = File.objects.filter(
        uploader = login_user,
        parent_folder = rootFolder
    )

    return JsonResponse({
        "message": "Success",
        "current_folder_id": rootFolder.id,
        "current_folder_name": "root/",
        "folder_results": list(folders.values()), #FolderListSerializer(folders, many=True),
        "file_results": list(files.values()), #FileListSerializer(files, many=True)
    }, json_dumps_params = {'ensure_ascii': True})

'''
폴더-파일 목록 조회: 어느 폴더에 들어갔을 때, 그 폴더에 존재하는 하위 폴더와 파일들의 목록 조회
GET: storage/get_folder_contents/
'''
@api_view(['GET'])
@authentication_classes((TokenAuthentication, ))
def get_folder_contents(request):
    login_user = request.user

    data = request.data
    folder_id = data.get("folder_id")       # 폴더 클릭해서 들어갔을 때, 클릭한 폴더의 PK
    folder_path = data.get("folder_path")

    # PK가 folder_id인 폴더 조회 
    clickedFolder = Folder.objects.get(
        pk = folder_id                  # PK가 folder_id
    )

    # parent_folder가 parentFolder인 폴더와 파일들 조회
    folders = Folder.objects.filter(
        creater = login_user,
        parent_folder = clickedFolder
    )

    files = File.objects.filter(
        uploader = login_user,
        parent_folder = clickedFolder
    )

    return JsonResponse({
        "message": "Success",
        "current_folder_id": folder_id,
        "current_folder_name": clickedFolder.foldername,
        "parent_folder_id": clickedFolder.parent_folder.id,
        "folder_results": list(folders.values()), 
        "file_results": list(files.values()), 
    }, json_dumps_params = {'ensure_ascii': True})

'''
업로드된 파일 메타데이터 전송: S3 업로드에 성공한 파일의 파일명 저장-PK 응답
POST: storage/upload_file/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def upload_file(request):
    login_user = request.user

    data = request.data
    filename = data.get("filename")
    parent_folder_id = data.get("parent_folder_id")
    #path = data.get("path")

    uploadedFile = File(
        filename = filename,
        uploader = login_user,
        parent_folder = Folder.objects.filter(
            creater = login_user,
            id = parent_folder_id
        )[0]
    )
    uploadedFile.save()

    return Response(FileSerializer(uploadedFile).data)

'''
파일명 변경: 업로드된 파일의 파일명 변경
POST: storage/modify_filename/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def modify_filename(request):
    login_user = request.user

    data = request.data
    file_id = data.get("file_id")
    src_name = data.get("src_name")
    dst_name = data.get("dst_name")
    parent_folder_id = data.get("parent_folder_id")
    _path = data.get("path")

    ## DB의 파일명 변경, modified_at 현재시간 삽입
    target = File.objects.filter(
        id = file_id,
        uploader = login_user
    )[0]
    target.filename = dst_name
    target.modified_at = timezone.now()
    target.save()

    ## S3의 객체 복사->기존 객체 삭제
    s3_key_path = str(login_user.user_id + "/" + _path)

    src_s3_object = {
        "Bucket": BucketName,
        "Key": s3_key_path + src_name
    }
    resource.meta.client.copy(src_s3_object, BucketName, s3_key_path + dst_name)

    client.delete_object(
        Bucket = BucketName,
        Key = s3_key_path + src_name
    )

    return JsonResponse({
        "message": "Success",
        "id": target.id,
        "filename": target.filename,
        "parent_folder_id": target.parent_folder.id,
        "path": _path,
        "created_at": target.created_at,
        "modified_at": target.modified_at
    }, json_dumps_params = {'ensure_ascii': True})

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
    # file의 PK - SQLite 삭제용
    # file이 있는 경로 - S3 삭제용
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
    s3_response = client.delete_object(Bucket=BucketName, Key=s3_object_key)
    
    # DB의 레코드 삭제
    filterFile.delete()
    
    return Response({"message": "success"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes((TokenAuthentication, ))
def delete_folder(request):
    user = request.user

    ## request에서 받아야 할 것
    # folder의 PK - SQLite 삭제용
    # 루트부터 folder까지의 경로 - S3 삭제용
    folder_id = request.data.get("folder_id")
    folder_path = request.data.get("folder_path")

    # S3의 객체 삭제
    bucket = resource.Bucket(BucketName)
    folder_prefix = str(user.user_id + "/" + folder_path)
    bucket.objects.filter(Prefix=folder_prefix).delete()

    # DB의 레코드 삭제 - cascade라 한 번만 하면 됨.
    Folder.objects.filter(
        creater = user,
        id = folder_id
    ).delete()
    
    return Response({"message": "success"}, status=status.HTTP_200_OK)
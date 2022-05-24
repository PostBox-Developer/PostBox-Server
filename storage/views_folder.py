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

    # parent_folder가 rootFolder인 폴더와 파일들 조회 && is_deleted: False
    folders = Folder.objects.filter(
        creater = login_user,
        parent_folder = rootFolder,
        is_deleted = False
    )

    files = File.objects.filter(
        uploader = login_user,
        parent_folder = rootFolder,
        is_deleted = False
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
        parent_folder = clickedFolder,
        is_deleted = False,
    )

    files = File.objects.filter(
        uploader = login_user,
        parent_folder = clickedFolder,
        is_deleted = False
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
폴더 생성: S3에 폴더 객체 생성 및 DB Folder 레코드 추가
POST: storage/create_folder/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def create_folder(request):
    login_user = request.user

    data = request.data
    parent_folder_id = data.get("parent_folder_id")
    _path = data.get("path")
    folder_name = data.get("folder_name")

    ## Folder 모델 생성 및 save
    createdFolder = Folder(
        foldername = folder_name,
        creater = login_user,
        parent_folder = Folder.objects.get(pk = parent_folder_id)
    )
    createdFolder.save()

    ## S3에 폴더 객체 생성
    s3_key = str(login_user.user_id + "/" + _path + folder_name)
    client.put_object(Bucket=BucketName, Key=s3_key)

    return JsonResponse({
        "message": "Success",
        "id": createdFolder.id,
        "folder_name": createdFolder.foldername,
        "parent_folder_id": createdFolder.parent_folder.id,
        "path": _path,
        "creater": createdFolder.creater.user_id,
        "created_at": createdFolder.created_at,
        "modified_at": createdFolder.modified_at
    }, json_dumps_params = {'ensure_ascii': True})

'''
폴더명 변경: S3 폴더 객체 복사-삭제 및 DB Folder 레코드 변경
POST: storage/modify_foldername/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def modify_foldername(request):
    login_user = request.user

    data = request.data
    folder_id = data.get("folder_id")
    src_name = data.get("src_name")
    dst_name = data.get("dst_name")
    _path = data.get("path")

    ## DB Folder.foldername 수정, modified_at 삽입
    targetFolder = Folder.objects.get(pk = folder_id)
    targetFolder.foldername = dst_name
    targetFolder.modified_at = timezone.now()
    targetFolder.save()

    ## S3 객체 복사 및 기존 객체 삭제
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
        "id": targetFolder.id,
        "folder_name": targetFolder.foldername,
        "parent_folder_id": targetFolder.parent_folder.id,
        "path": _path,
        "creater": targetFolder.creater.user_id,
        "created_at": targetFolder.created_at,
        "modified_at": targetFolder.modified_at
    }, json_dumps_params = {'ensure_ascii': True})
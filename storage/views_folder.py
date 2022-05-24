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

    # parent_folder가 rootFolder인 폴더와 파일들 조회 && is_deleted: 0
    folders = Folder.objects.filter(
        creater = login_user,
        parent_folder = rootFolder,
        is_deleted = 0
    )

    files = File.objects.filter(
        uploader = login_user,
        parent_folder = rootFolder,
        is_deleted = 0
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
        is_deleted = 0
    )

    files = File.objects.filter(
        uploader = login_user,
        parent_folder = clickedFolder,
        is_deleted = 0
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

    bucket = resource.Bucket(BucketName)

    # 복사
    for obj in bucket.objects.filter(Prefix=s3_key_path + src_name):
        old_source = {"Bucket": BucketName, "Key": obj.key}
        new_key = obj.key.replace(s3_key_path + src_name, s3_key_path + dst_name, 1)
        new_obj = bucket.Object(new_key)
        new_obj.copy(old_source)

    # 삭제
    bucket = resource.Bucket(BucketName)
    bucket.objects.filter(Prefix=(s3_key_path + src_name)).delete()

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

'''
폴더 이동: S3 폴더 객체 복사-삭제 및 DB Folder 레코드 변경
POST: storage/move_folder/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def move_folder(request):
    login_user = request.user

    data = request.data
    folder_id = data.get("folder_id")
    folder_name = data.get("folder_name")
    src_parent_folder_id = data.get("src_parent_folder_id")
    dst_parent_folder_id = data.get("dst_parent_folder_id")
    src_path = data.get("src_path")
    dst_path = data.get("dst_path")

    ## DB Folder.parent_folder 수정, modified_at 삽입
    targetFolder = Folder.objects.get(pk = folder_id)
    targetFolder.parent_folder = Folder.objects.get(pk = dst_parent_folder_id)
    targetFolder.modified_at = timezone.now()
    targetFolder.save()

    ## S3 객체 복사 및 기존 객체 삭제
    s3_src_path = str(login_user.user_id + "/" + src_path + folder_name)
    s3_dst_path = str(login_user.user_id + "/" + dst_path + folder_name)

    bucket = resource.Bucket(BucketName)

    # 복사
    for obj in bucket.objects.filter(Prefix=s3_src_path):
        old_source = {"Bucket": BucketName, "Key": obj.key}
        new_key = obj.key.replace(s3_src_path, s3_dst_path, 1)
        new_obj = bucket.Object(new_key)
        new_obj.copy(old_source)

    # 삭제
    bucket = resource.Bucket(BucketName)
    bucket.objects.filter(Prefix=s3_src_path).delete()

    return JsonResponse({
        "message": "Success",
        "id": targetFolder.id,
        "folder_name": targetFolder.foldername,
        "parent_folder_id": targetFolder.parent_folder.id,
        "path": dst_path,
        "creater": targetFolder.creater.user_id,
        "created_at": targetFolder.created_at,
        "modified_at": targetFolder.modified_at
    }, json_dumps_params = {'ensure_ascii': True})


'''
폴더를 휴지통으로: DB Folder.is_deleted 및 하위 Folder.is_deleted, File.is_deleted 변경
POST: storage/move_folder_trashcan/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def move_folder_trashcan(request):
    
    data = request.data
    folder_id = data.get("folder_id")

    ## pk=folder_id인 폴더의 is_deleted: 1, 하위 폴더와 파일들의 is_deleted: 2
    targetFolder = Folder.objects.get(pk = folder_id)
    targetFolder.is_deleted = 1
    targetFolder.modified_at = timezone.now()
    targetFolder.save()

    # 하위 파일들
    sub_files = File.objects.filter(parent_folder=targetFolder)
    sub_files.update(is_deleted = 2)
    sub_files.update(modified_at = timezone.now())

    return 1

'''
휴지통 폴더 복구: DB Folder.is_deleted 및 하위 Folder.is_deleted, File.is_deleted 변경
POST: storage/restore_folder/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def restore_folder(request):
    data = request.data
    folder_id = data.get("folder_id")

    # pk=folder_id인 폴더의 is_deleted: 0, 하위 폴더와 파일들의 is_deleted: 0
    
    return 1

'''
폴더 영구 삭제: S3 폴더 객체 삭제 및 DB Folder 레코드 삭제
POST: storage/delete_folder/
'''
@api_view(['DELETE'])
@authentication_classes((TokenAuthentication, ))
def delete_folder(request):
    user = request.user

    data = request.data
    folder_id = data.get("folder_id")
    folder_name = data.get("folder_name")
    parent_folder_id = data.get("parent_folder_id")
    path = data.get("path")

    # S3의 객체 삭제
    bucket = resource.Bucket(BucketName)
    folder_prefix = str(user.user_id + "/" + path + folder_name)
    bucket.objects.filter(Prefix=folder_prefix).delete()

    # DB의 레코드 삭제 - cascade라 한 번만 하면 됨.
    Folder.objects.get(
        pk = folder_id
    ).delete()
    
    return Response({"message": "success"}, status=status.HTTP_200_OK)
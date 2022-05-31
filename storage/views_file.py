from pydoc import cli
from .models import File, Folder, FolderSharing
from .serializers import *
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404

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
    target = File.objects.get(
        pk = file_id,
    )
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
        "uploader": target.uploader,
        "created_at": target.created_at,
        "modified_at": target.modified_at
    }, json_dumps_params = {'ensure_ascii': True})

'''
저장 위치 변경: 업로드된 파일의 위치(경로) 변경
POST: storage/move_file/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def move_file(request):
    login_user = request.user

    data = request.data
    file_id = data.get("file_id")
    filename = data.get("filename")
    src_parent_folder_id = data.get("src_parent_folder_id")
    dst_parent_folder_id = data.get("dst_parent_folder_id")
    src_path = data.get("src_path")
    dst_path = data.get("dst_path")

    ## DB의 File.parent_folder 변경, modified_at 현재시간 삽입
    target = File.objects.get(
        pk = file_id
    )
    target.parent_folder = Folder.objects.get(pk = dst_parent_folder_id)
    target.modified_at = timezone.now()
    target.save()

    ## S3의 객체 복사->기존 객체 삭제
    s3_src_path = str(login_user.user_id + "/" + src_path)
    s3_dst_path = str(login_user.user_id + "/" + dst_path)

    src_s3_object = {
        "Bucket": BucketName,
        "Key": s3_src_path + filename
    }
    resource.meta.client.copy(src_s3_object, BucketName, s3_dst_path + filename)

    client.delete_object(
        Bucket = BucketName,
        Key = s3_src_path + filename
    )

    return JsonResponse({
        "message": "Success",
        "id": target.id,
        "filename": target.filename,
        "dst_parent_folder_id": target.parent_folder.id,
        "dst_path": dst_path,
        "uploader": target.uploader.user_id,
        "created_at": target.created_at,
        "modified_at": target.modified_at
    }, json_dumps_params = {'ensure_ascii': True})

'''
파일을 휴지통으로: 업로드된 파일을 휴지통으로 보내 임시 삭제
POST: storage/move_file_trashcan/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def move_file_trashcan(request):
    login_user = request.user

    data = request.data
    file_id = data.get("file_id")

    ## DB의 File.is_deleted -> 1로 변경
    target = File.objects.get(
        pk = file_id
    )
    target.is_deleted = 0
    target.save()

    return JsonResponse({
        "message": "Success"
    }, json_dumps_params = {'ensure_ascii': True})

'''
파일을 휴지통으로: 업로드된 파일을 휴지통으로 보내 임시 삭제
POST: storage/restore_file/
'''
@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def restore_file(request):
    login_user = request.user

    data = request.data
    file_id = data.get("file_id")

    ## DB의 File.is_deleted -> 1로 변경
    target = File.objects.get(
        pk = file_id
    )
    target.is_deleted = 1
    target.save()

    return JsonResponse({
        "message": "Success"
    }, json_dumps_params = {'ensure_ascii': True})

'''
파일 영구 삭제: 업로드된 파일을 S3와 DB 모두에서 삭제
DELETE: storage/delete_file/
'''
@api_view(['DELETE'])
@authentication_classes((TokenAuthentication, ))
def delete_file(request):
    login_user = request.user

    data = request.data
    file_id = data.get("file_id")
    filename = data.get("filename")
    parent_folder_id = data.get("parent_folder_id")
    _path = data.get("path")

    ## S3의 객체 삭제
    target_path = str(login_user.user_id + "/" + _path)
    client.delete_object(
        Bucket = BucketName,
        Key = target_path + filename
    )

    ## DB의 File 레코드 삭제
    target = File.objects.get(
        pk = file_id
    )
    target.delete()

    return JsonResponse({
        "message": "Success"
    }, json_dumps_params = {'ensure_ascii': True})



@api_view(['GET'])
@authentication_classes((TokenAuthentication, ))
def check_permission(request):
    user_id = request.user.user_id
    parent_folder_id = request.data.get('parent_folder_id')
    request_type = request.data.get('type')
    file_name = request.data.get('filename')
    path = request.data.get('path')
    if request_type == 'upload':
        request_type = 'put_object'
    elif request_type == 'download':
        request_type = 'get_object'

    folder = get_object_or_404(Folder, pk=parent_folder_id)

    if folder.is_deleted == True:
        return JsonResponse({
            "message": "Folder is deleted."
        }, json_dumps_params = {'ensure_ascii': True}
        , status=400)
    
    if folder.is_shared == False:
        if folder.creater == request.user:
            url = client.generate_presigned_url(
                ClientMethod=request_type, 
                Params={'Bucket': BucketName, 'Key': user_id + '/' + path + file_name},
                ExpiresIn=300)

            return JsonResponse(
                {"url": url},
                json_dumps_params = {'ensure_ascii': True},
                status=200
            )
    else:
        r_folder = folder
        while r_folder.parent_folder != None:
            r_folder = r_folder.parent_folder
        folder_sharing = get_object_or_404(FolderSharing, folder=r_folder, sharer=request.user)
        
        if folder_sharing.permission != 0 or request_type == 'get_object':
            url = client.generate_presigned_url(
                ClientMethod=request_type, 
                Params={'Bucket': BucketName, 'Key': 'shared_' + user_id + '/' + path + file_name},
                ExpiresIn=300)
            
            return JsonResponse(
                {"url": url},
                json_dumps_params = {'ensure_ascii': True},
                status=200
            )

    return JsonResponse(
        {"message": "permission fail"},
        json_dumps_params = {'ensure_ascii': True},
        status=400
    )
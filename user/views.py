from typing import Any
from django.http import JsonResponse
from rest_framework import generics
from user import serializers
from user.models import User, UserFollowing
from user.serializers import LoginSerializer, UserDataSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import exceptions
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
import json
from django.db import IntegrityError
from django.core.serializers import json as JSON
from storage.models import Folder
import boto3
from .image_bucket_config import secrets
import re


client = boto3.client('s3',
                        aws_access_key_id = secrets["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key = secrets["AWS_SECRET_ACCESS_KEY"],
                        region_name = secrets["AWS_DEFAULT_REGION"])

resource = boto3.resource('s3',
                        aws_access_key_id = secrets["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key = secrets["AWS_SECRET_ACCESS_KEY"],
                        region_name = secrets["AWS_DEFAULT_REGION"])

BucketName = secrets["BUCKET_NAME"]

# class UserAPI(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

@api_view(['POST'])
def sign_up(request):
    user_id = request.data.get('user_id')
    username = request.data.get('username')
    password = request.data.get('password')

    if len(user_id) < 6:
        raise exceptions.ParseError("User_id is too short.")
    elif len(password) < 8:
        raise exceptions.ParseError("Password is too short.")
    elif re.match('\w+', user_id) != user_id:
        raise exceptions.ParseError("special characters in user_id.")

    user = User.objects.create_user(user_id=user_id, username=username, password=password)

    # root_folder 생성 및 연결
    root_folder = Folder.objects.create(foldername=user_id+"'s root", creater=user)
    user.root_folder = root_folder
    user.save()

    return JsonResponse({
        'pk': user.pk,
        'user_id': user.user_id,
        'username': user.username,
        'root_folder': user.root_folder.pk,
        'profile_image_url': user.profile_image_url
    }, json_dumps_params = {'ensure_ascii': False})

class LoginAPI(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({
            'token': token.key,
            'pk': user.pk,
            'user_id': user.user_id,
            'username': user.username,
            'root_folder': user.root_folder.pk,
            'profile_image_url': user.profile_image_url
        }, json_dumps_params = {'ensure_ascii': False})

# class UserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

@api_view(['GET'])
def user_detail(request, user_id):
    user = get_object_or_404(User, user_id=user_id)

    return JsonResponse({
        'pk': user.pk,
        'user_id': user.user_id,
        'username': user.username,
        'root_folder': user.root_folder.pk,
        'profile_image_url': user.profile_image_url
    }, json_dumps_params = {'ensure_ascii': False})


@api_view(['PUT'])
@authentication_classes((TokenAuthentication, ))
def user_update(request, user_id):
    user = get_object_or_404(User, user_id=user_id)

    username = request.data.get('username')
    # src_profile_img_url = request.data.get("src_profile_image_url")
    dst_profile_img = request.FILES["dst_profile_image_name"]

    # 이미지 수정
    if dst_profile_img != None:
        bucket = resource.Bucket(BucketName)

        # src_index = src_profile_img_url.find('user_profile/')
        # s3_src_key = str(src_profile_img_url[src_index:-1])
        s3_dst_key = 'user_profile/' + user.user_id
        bucket.upload_fileobj(dst_profile_img, s3_dst_key)

    # db 수정
    user.username = username
    user.profile_image_url = 'https://' + secrets['BUCKET_NAME'] + '.s3.' + secrets['AWS_DEFAULT_REGION'] + '.amazonaws.com/' + s3_dst_key
    user.save()

    return JsonResponse({
        'pk': user.pk,
        'user_id': user.user_id,
        'username': user.username,
        'root_folder': user.root_folder.pk,
        'profile_image_url': user.profile_image_url
    }, json_dumps_params = {'ensure_ascii': False})


@api_view(['DELETE'])
@authentication_classes((TokenAuthentication, ))
def user_delete(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    
    # 재확인
    if user.pk == request.user.pk:
        user.delete()

        return JsonResponse({
            'message': 'success'
        }, json_dumps_params = {'ensure_ascii': False})
    else:
        return JsonResponse({
            'message': 'fail'
        }, json_dumps_params = {'ensure_ascii': False}
        , status=404)



# ------------friend------------

@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def friend_create(request):
    follower = get_object_or_404(User, pk=request.user.pk)
    followee = get_object_or_404(User, pk=request.data.get('followee'))
    
    try:
        user_following_obj = UserFollowing.objects.create(follower=follower, followee=followee)

    except IntegrityError as e: 
        raise exceptions.ParseError("Already exists.")
            

    response = {
        'userFollowing': {
            'pk': user_following_obj.pk,
            'follower': {
                'pk': user_following_obj.follower.pk,
                'user_id': user_following_obj.follower.user_id,
                'username': user_following_obj.follower.username,
                'root_folder': user_following_obj.follower.root_folder.pk,
                'profile_image_url': user_following_obj.follower.profile_image_url
            },
            'followee': {
                'pk': user_following_obj.followee.pk,
                'user_id': user_following_obj.followee.user_id,
                'username': user_following_obj.followee.username,
                'root_folder': user_following_obj.followee.root_folder.pk,
                'profile_image_url': user_following_obj.followee.profile_image_url
            },
    }}

    # response_json = json.dumps(response)
    # print(response_json)
    return JsonResponse(response, json_dumps_params = {'ensure_ascii': False}, safe=False)


@api_view(['DELETE'])
@authentication_classes((TokenAuthentication, ))
def friend_delete(request, userFollowing_pk):
    user_following = get_object_or_404(UserFollowing, pk=userFollowing_pk)
    
    # 재확인
    if user_following.follower.pk != request.user.pk:
        return JsonResponse({
            'message': 'fail'
        }, json_dumps_params = {'ensure_ascii': False}
        , status=400)
    else:
        user_following.delete()

        return JsonResponse({
            'message': 'success'
        }, json_dumps_params = {'ensure_ascii': False}
        , status=204)


@api_view(['GET'])
def followee_list(request):
    target_user = get_object_or_404(User, pk=request.data.get('target_user'))
    
    user_following_set = UserFollowing.objects.filter(follower=target_user)
    
    userdata_serializer = UserDataSerializer(target_user)
    response_target_user = userdata_serializer.data

    user_following_list = []
    for user_following in user_following_set:
        followee_serializer = UserDataSerializer(user_following.followee)
        followee_data = followee_serializer.data
        user_following_list.append({'pk': user_following.pk, 'followee': followee_data})
    
    response = {
        'target_user': response_target_user,
        'userFollowing_list': user_following_list
    }

    return JsonResponse(response, json_dumps_params = {'ensure_ascii': False}, safe=False)


@api_view(['GET'])
def follower_list(request):
    target_user = get_object_or_404(User, pk=request.data.get('target_user'))
    
    user_following_set = UserFollowing.objects.filter(followee=target_user)
    
    userdata_serializer = UserDataSerializer(target_user)
    response_target_user = userdata_serializer.data

    user_following_list = []
    for user_following in user_following_set:
        follower_serializer = UserDataSerializer(user_following.follower)
        follower_data = follower_serializer.data
        user_following_list.append({'pk': user_following.pk, 'followee': follower_data})
    
    response = {
        'target_user': response_target_user,
        'userFollowing_list': user_following_list
    }

    return JsonResponse(response, json_dumps_params = {'ensure_ascii': False}, safe=False)

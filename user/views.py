from django.http import JsonResponse
from rest_framework import generics
from user.models import User
from user.serializers import LoginSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import exceptions
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication


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
    elif ('/' in user_id):
        raise exceptions.ParseError("'/' in user_id.")

    user = User.objects.create(user_id=user_id, username=username, password=password)

    return JsonResponse({
        'pk': user.pk,
        'user_id': user.user_id,
        'username': user.username,
        'root_folder': user.root_folder,
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
            'root_folder': user.root_folder,
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
        'root_folder': user.root_folder,
        'profile_image_url': user.profile_image_url
    }, json_dumps_params = {'ensure_ascii': False})


@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
def user_update(request, user_id):
    user = get_object_or_404(User, user_id=user_id)

    username = request.data.get('username')
    src_profile_img_url = request.data.get("src_profile_image_url")
    dst_profile_img_name = request.FILES["dst_profile_image_name"]

    # 이미지 수정
    # if dst_profile_img_name != None:
    #     src_index = src_profile_img_url.find('user_profile/')
    #     s3_src_key = str(src_profile_img_url[src_index:-1])
    #     s3_dst_key = str('user_profile/' + user.user_id + '/' + dst_profile_img_name)

    #     src_s3_object = {
    #         "Bucket": BucketName
    #     }

    # db 수정
    user.username = username
    # user.profile_image_url = dst_profile_img_url
    user.save()

    return JsonResponse({
        'pk': user.pk,
        'user_id': user.user_id,
        'username': user.username,
        'root_folder': user.root_folder,
        'profile_image_url': user.profile_image_url
    }, json_dumps_params = {'ensure_ascii': False})
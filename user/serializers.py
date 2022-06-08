from rest_framework import serializers
from user.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'user_id', 'username', 'password', 'root_folder', 'profile_image_url']

    def create(self, validated_data):
        user = User.objects.create_user(
            user_id = validated_data['user_id'],
            username = validated_data['username'],
            password = validated_data['password']
        )
        return user
        
class LoginSerializer(serializers.Serializer):
    user_id = serializers.CharField(
        label=_("User_id"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        password = attrs.get('password')

        if user_id and password:
            user = authenticate(request=self.context.get('request'),
                                user_id=user_id, password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "user_id" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'user_id', 'username', 'root_folder', 'profile_image_url']
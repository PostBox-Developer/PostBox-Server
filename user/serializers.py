from rest_framework import serializers
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'root_folder', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            user_id = validated_data['user_id'],
            username = validated_data['username'],
            password = validated_data['password']
        )
        return user

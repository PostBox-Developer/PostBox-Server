from .models import Post
# user.serializer import userserializer
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "desc",
            "author_id",    #   User의 user_id
            "author_name",  #   User의 username
            "created_at",
            "modified_at",
        ]

    author_id = serializers.SerializerMethodField("getAuthorId")
    author_name = serializers.SerializerMethodField("getAuthorName")

    def getAuthorId(self, obj):
        return obj.author.user_id

    def getAuthorName(self, obj):
        return obj.author.username
from rest_framework import permissions

class IsAuthorOfPost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsOwnerOfPostImage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.post.author == request.user

class IsOwnerOfCategory(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
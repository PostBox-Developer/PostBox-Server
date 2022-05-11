from django.contrib import admin
from user.models import User, UserFollowing


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username']
    list_display_links = ['user_id', 'username']


@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = ['follower', 'followee']
    list_display_links = ['follower', 'followee']
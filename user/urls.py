from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.sign_up),
    path('login/', views.LoginAPI.as_view()),
    path('detail/<str:user_id>/', views.user_detail),
    path('update/<str:user_id>/', views.user_update),
    path('delete/<str:user_id>/', views.user_delete),
    path('friend/create/', views.friend_create),
    path('friend/delete/<int:userFollowing_pk>/', views.friend_delete),
    path('friend/followee-list/', views.followee_list),
    path('friend/follower-list/', views.follower_list),
]

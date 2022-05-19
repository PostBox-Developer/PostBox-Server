from django.urls import path, include
from . import views

app_name = "post"

urlpatterns = [
    path("", views.PostAPI.as_view()),
    path("<int:pk>/", views.PostDetailAPI.as_view()),
    path("post-attach-file/create/", views.PostAttachFileCreateAPI.as_view()),
    path("post-attach-file/delete/<int:pk>/", views.PostAttachFileDeleteAPI.as_view()),
]
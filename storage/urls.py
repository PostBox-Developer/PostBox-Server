from django.urls import path, include
from . import views

app_name = "storage"

urlpatterns = [
    path("get_file_list/", views.FileAPIView.as_view()),
    path("get_folder_list/", views.FolderAPIView.as_view()),
    path("upload_file/", views.FileAPIView.as_view()),
    path("create_new_folder/", views.FolderAPIView.as_view()),
]
from django.urls import path, include
from . import views

app_name = "storage"

urlpatterns = [
    path("get_home_folder/", views.get_home_folder),
    path("get_folder_contents/", views.get_folder_contents),
    path("upload_file/", views.upload_file),
    path("modify_filename/", views.modify_filename),

    path("get_file_list/", views.FileListCreateAPIView.as_view()),
    path("get_folder_list/", views.FolderListCreateAPIView.as_view()),
    #path("upload_file/", views.FileListCreateAPIView.as_view()),
    path("create_new_folder/", views.FolderListCreateAPIView.as_view()),


    path("delete_file/", views.delete_file),
    path("delete_folder/", views.delete_folder),
]
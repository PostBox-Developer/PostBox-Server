from django.urls import path, include
from . import views_file
from . import views_folder

app_name = "storage"

urlpatterns = [

    # Files
    path("upload_file/", views_file.upload_file),
    path("modify_filename/", views_file.modify_filename),
    path("move_file/", views_file.move_file),
    path("move_file_trashcan/", views_file.move_file_trashcan),
    path("restore_file/", views_file.restore_file),
    path("delete_file/", views_file.delete_file),

    #Folders
    path("get_home_folder/", views_folder.get_home_folder),
    path("get_folder_contents/", views_folder.get_folder_contents),
    path("create_folder/", views_folder.create_folder),
    path("modify_foldername/", views_folder.modify_foldername),

    path("get_file_list/", views_file.FileListCreateAPIView.as_view()),
    path("get_folder_list/", views_file.FolderListCreateAPIView.as_view()),
    #path("upload_file/", views_file.FileListCreateAPIView.as_view()),
    path("create_new_folder/", views_file.FolderListCreateAPIView.as_view()),


    
    path("delete_folder/", views_file.delete_folder),
]
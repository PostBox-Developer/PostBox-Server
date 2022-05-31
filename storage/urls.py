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
    path("move_folder/", views_folder.move_folder),
    path("move_folder_trashcan/", views_folder.move_folder_trashcan),
    path("restore_folder/", views_folder.restore_folder),
    path("delete_folder/", views_folder.delete_folder),
    path("get_trashcan_contents/", views_folder.get_trashcan_contents),
    path("set_folder_open_scope/", views_folder.set_folder_open_scope),
    path("create_shared_folder/", views_folder.create_shared_folder),
    path("add_folder_sharer/", views_folder.add_folder_sharer),
    path("delete_folder_sharer/", views_folder.delete_folder_sharer),
    path("get_folder_sharer/", views_folder.get_folder_sharer),
]
from django.urls import path, include
from . import views

app_name = "storage"

urlpatterns = [
    path("get_file_list/", views.FileAPIView.as_view()),
    path("get_folder_list/", views.FolderAPIView.as_view()),
]
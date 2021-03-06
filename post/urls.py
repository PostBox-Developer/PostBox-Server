from django.urls import path, include
from . import views

app_name = "post"

urlpatterns = [
    path("post/", views.PostListAPI.as_view()),
    path("post/create/", views.PostCreateAPI.as_view()),
    path("post/<int:pk>/", views.post_detail),
    path("post/<int:pk>/update/", views.PostUpdateAPI.as_view()),
    path("post/<int:pk>/attach-file/", views.post_attach_file),
    path("post/<int:pk>/delete/", views.PostDeleteAPI.as_view()),
    path("post-image/<int:pk>/delete/", views.PostImageDeleteAPI.as_view()),
    path("category/", views.CatecoryListAPI.as_view()),
    path("category/create/", views.CatecoryCreateAPI.as_view()),
    path("category/<int:pk>/rename/", views.CatecoryRenameAPI.as_view()),
    path("category/<int:pk>/delete/", views.CatecoryDeleteAPI.as_view()),
]
from django.urls import path, include
from . import views

app_name = "post"

urlpatterns = [
    path("post/", views.PostAPI.as_view()),
    path("post/<int:pk>/", views.PostDetailAPI.as_view()),
]
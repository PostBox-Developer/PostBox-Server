from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.UserAPI.as_view()),
    path('login/', views.LoginAPI.as_view()),
]

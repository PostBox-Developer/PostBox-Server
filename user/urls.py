from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.UserCreate.as_view()),
]

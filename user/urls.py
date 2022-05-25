from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.sign_up),
    path('login/', views.LoginAPI.as_view()),
    path('detail/<str:user_id>/', views.user_detail),
    path('update/<str:user_id>/', views.user_update),
]

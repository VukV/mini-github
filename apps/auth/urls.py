from django.urls import path

from apps.auth import views

urlpatterns = [
    path('', views.test, name='welcome'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
]

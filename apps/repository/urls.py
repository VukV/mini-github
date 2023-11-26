from django.urls import path

from apps.authentication import views as auth_views
from apps.repository import views


urlpatterns = [
    path('repository/<int:repository_id>/', views.repository_detail, name='repository'),
    path('create-repository/', views.create_repository, name='create_repository'),
]

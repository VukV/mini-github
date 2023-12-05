from django.urls import path

from apps.authentication import views as auth_views
from apps.repository import views


urlpatterns = [
    path('<int:repository_id>/', views.repository_detail, name='repository'),
    path('create-repository/', views.create_repository, name='create_repository'),
    path('settings/<int:repository_id>/', views.repository_settings, name='repository_settings'),
    path('delete/<int:repository_id>/', views.delete_repository, name='delete_repository'),
    path('visibility/<int:repository_id>/', views.change_repository_visibility, name='change_repository_visibility'),
    path('rename/<int:repository_id>/', views.rename_repository, name='rename_repository'),
    path('add_collaborator/<int:repository_id>/', views.add_collaborator, name='add_collaborator'),
    path('remove_collaborator/<int:repository_id>/<int:user_id>/', views.remove_collaborator, name='remove_collaborator'),
]

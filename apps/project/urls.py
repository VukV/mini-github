from django.urls import path

from apps.project import views

urlpatterns = [
    path('<int:repository_id>/', views.projects_from_repository, name='repository_projects'),
    path('<int:repository_id>/<int:project_id>', views.project_detail, name='project_detail'),
    path('<int:repository_id>/create_project', views.add_project, name='add_project'),
    path('<int:repository_id>/edit_project/<int:project_id>', views.edit_project, name='edit_project'),
    path('<int:repository_id>/delete_project/<int:project_id>', views.delete_project, name='delete_project'),
]

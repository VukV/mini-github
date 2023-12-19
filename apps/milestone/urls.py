from django.urls import path

from apps.milestone import views

urlpatterns = [
    path('<int:repository_id>/', views.milestones_from_repository, name='repository_milestones'),
    path('<int:repository_id>/create_milestone/', views.add_milestone, name='add_milestone'),
    path('<int:repository_id>/edit_milestone/<int:milestone_id>', views.edit_milestone, name='edit_milestone'),
    path('<int:repository_id>/delete_milestone/<int:milestone_id>', views.delete_milestone, name='delete_milestone'),
    path('<int:repository_id>/close_milestone/<int:milestone_id>', views.close_milestone, name='close_milestone'),
]

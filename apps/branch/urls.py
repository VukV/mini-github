from django.urls import path

from apps.branch import views

urlpatterns = [
    path('<int:repository_id>/', views.branches_from_repository, name='repository_branches'),
    path('<int:repository_id>/create_branch/', views.add_branch, name='add_branch'),
    path('<int:repository_id>/edit_branch/<int:branch_id>', views.edit_branch, name='edit_branch'),
    path('<int:repository_id>/delete_branch/<int:branch_id>', views.delete_branch, name='delete_branch'),
]

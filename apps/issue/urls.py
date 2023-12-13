from django.urls import path

from apps.issue import views

urlpatterns = [
    path('<int:repository_id>/', views.issues_from_repository, name='repository_issues'),
    path('<int:repository_id>/<int:issue_id>', views.issue_detail, name='issue_detail'),
    path('<int:repository_id>/create_issue', views.add_issue, name='add_issue'),
    path('<int:repository_id>/close_issue/<int:issue_id>', views.close_issue, name='close_issue'),
    path('<int:repository_id>/edit_issue/<int:issue_id>', views.edit_issue, name='edit_issue'),
    path('<int:repository_id>/delete_issue/<int:issue_id>', views.delete_issue, name='delete_issue'),
    path('project/<int:repository_id>/issue/<int:issue_id>/todo/', views.move_issue_to_todo, name='move_issue_todo'),
    path('project/<int:repository_id>/issue/<int:issue_id>/in_progress/', views.move_issue_to_in_progress, name='move_issue_in_progress'),
    path('project/<int:repository_id>/issue/<int:issue_id>/done/', views.move_issue_to_done, name='move_issue_done'),
]

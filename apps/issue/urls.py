from django.urls import path

from apps.issue import views

urlpatterns = [
    path('<int:repository_id>/', views.issues_from_repository, name='repository_issues'),
    path('<int:repository_id>/<int:issue_id>', views.issue_detail, name='issue_detail'),
    path('<int:repository_id>/create_issue', views.add_issue, name='add_issue'),
]

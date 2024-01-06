from django.urls import path

from apps.commit import views

urlpatterns = [
    path('<int:branch_id>/', views.commits_from_branch, name='branch_commits'),
    path('<int:branch_id>/create_commit/', views.add_commit, name='add_commit'),
]

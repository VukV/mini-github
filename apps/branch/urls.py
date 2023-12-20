from django.urls import path

from apps.branch import views

urlpatterns = [
    path('<int:repository_id>/', views.branches_from_repository, name='repository_branches'),
]

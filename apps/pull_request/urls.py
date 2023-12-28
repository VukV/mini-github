from django.urls import path

from apps.pull_request import views

urlpatterns = [
    path('<int:repository_id>/', views.pull_requests_from_repository, name='repository_pull_requests'),
    path('<int:repository_id>/create_pull_request/', views.add_pull_request, name='add_pull_request'),
    path('<int:repository_id>/<int:pr_id>', views.pull_request_detail, name='pull_request_detail'),
    path('<int:repository_id>/merge/<int:pr_id>', views.merge_pull_request, name='merge_pull_request'),
    path('<int:repository_id>/close/<int:pr_id>', views.close_pull_request, name='close_pull_request'),
    path('<int:repository_id>/approve/<int:pr_id>', views.approve_pull_request, name='approve_pull_request'),
]

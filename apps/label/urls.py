from django.urls import path

from apps.label import views


urlpatterns = [
    path('<int:repository_id>/', views.labels_from_repository, name='repository_labels'),
]

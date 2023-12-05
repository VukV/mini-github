from django.urls import path

from apps.label import views


urlpatterns = [
    path('<int:repository_id>/', views.labels_from_repository, name='repository_labels'),
    path('<int:repository_id>/create_label/', views.add_label, name='add_label'),
    path('<int:repository_id>/edit_label/<int:label_id>', views.edit_label, name='edit_label'),
    path('<int:repository_id>/delete_label/<int:label_id>', views.delete_label, name='delete_label'),
]

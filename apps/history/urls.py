from django.urls import path

from apps.history import views

urlpatterns = [
    path('<int:repository_id>/', views.repository_insights, name='repository_insights'),
]

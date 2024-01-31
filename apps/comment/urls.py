from django.urls import path
from apps.comment import views


urlpatterns = [
    path('add_comment/<int:pr_id>/', views.add_comment, name='add_comment'),
    path('reply_comment/<int:pr_id>/<int:comment_id>', views.reply_comment, name='reply_comment'),
]

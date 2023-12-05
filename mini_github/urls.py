"""
URL configuration for mini_github project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from mini_github import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('apps.authentication.urls')),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('branch/', include('apps.branch.urls')),
    path('commit/', include('apps.commit.urls')),
    path('history/', include('apps.history.urls')),
    path('issue/', include('apps.issue.urls')),
    path('label/', include('apps.label.urls')),
    path('milestone/', include('apps.milestone.urls')),
    path('project/', include('apps.project.urls')),
    path('pull-request/', include('apps.pull_request.urls')),
    path('repository/', include('apps.repository.urls')),
]

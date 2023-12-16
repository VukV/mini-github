from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from apps.repository.models import Repository
from apps.history.models import History
from django.db.models import Q


@login_required()
@cache_page(60 * 15)
def home(request):
    return render(request, 'home/home.html')


@login_required()
def dashboard(request):
    current_user = request.user

    repositories = Repository.objects.filter(
        Q(owner=current_user) | Q(collaborators=current_user)
    ).distinct()
    recent_activity = History.objects.filter(user_changed=current_user).order_by('-date_time_changed')[:5]

    context = {
        'repositories': repositories,
        'recent_activity': recent_activity,
    }

    return render(request, 'home/dashboard.html', context)

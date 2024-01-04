from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from apps.commit.models import Commit
from apps.issue.models import Issue
from apps.pull_request.models import PullRequest
from apps.repository.models import Repository
from apps.history.models import History
from django.db.models import Q


@login_required()
@cache_page(60 * 15)
@vary_on_cookie
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


@login_required()
def search(request):
    query = request.GET.get('q', '')
    user = request.user

    cache_key = f'search_results_{query}_{user.id}'
    context = cache.get(cache_key)

    if not context:
        repositories = Repository.objects.filter(
            Q(public=True) | Q(owner=user) | Q(collaborators__in=[user])
        ).distinct()

        issues = Issue.objects.filter(
            Q(repository__public=True) |
            Q(repository__owner=user) |
            Q(repository__collaborators__in=[user])
        ).distinct()

        pull_requests = PullRequest.objects.filter(
            Q(repository__public=True) |
            Q(repository__owner=user) |
            Q(repository__collaborators__in=[user])
        ).distinct()

        commits = Commit.objects.filter(
            Q(repository__public=True) |
            Q(repository__owner=user) |
            Q(repository__collaborators__in=[user])
        ).distinct()

        if query:
            repositories = repositories.filter(name__icontains=query)
            issues = issues.filter(name__icontains=query)
            pull_requests = pull_requests.filter(name__icontains=query)
            commits = commits.filter(message__icontains=query)

        context = {
            'repositories': repositories,
            'issues': issues,
            'pull_requests': pull_requests,
            'commits': commits,
            'query': query,
        }

        cache.set(cache_key, context, timeout=2*60)

    return render(request, 'home/search_results.html', context)

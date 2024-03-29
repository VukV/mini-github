from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.timezone import localtime

from apps.history.models import History
from apps.repository.models import Repository


@login_required()
def repository_insights(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    period = request.GET.get('period', '1 week')
    delta = timedelta(weeks=1)

    if period == '24h':
        delta = timedelta(hours=24)
    elif period == '1 week':
        delta = timedelta(weeks=1)
    elif period == '1 month':
        delta = timedelta(weeks=4)

    start_date = timezone.now() - delta

    cache_key = f'repository_{repository_id}_insights_{period}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'repository/insights/repository_insights.html', cached_data)

    history_items = History.objects.filter(
        date_time_changed__gte=start_date,
        repository=repository
    )

    merged_prs = history_items.filter(type='pull request', changed_action='merged').count()
    opened_prs = history_items.filter(type='pull request', changed_action='opened').count()
    closed_issues = history_items.filter(type='issue', changed_action='closed').count()
    opened_issues = history_items.filter(type='issue', changed_action='opened').count()

    # Prepare data for the commit graph
    commits = history_items.filter(type='commit')
    commit_counts = defaultdict(int)
    for commit in commits:
        date = localtime(commit.date_time_changed).date()
        commit_counts[date] += 1
    sorted_dates = sorted(commit_counts)
    sorted_counts = [commit_counts[date] for date in sorted_dates]

    render_object = {
        'repository': repository,
        'merged_prs': merged_prs,
        'opened_prs': opened_prs,
        'closed_issues': closed_issues,
        'opened_issues': opened_issues,
        'commits': commits,
        'commit_dates': [date.strftime("%Y-%m-%d") for date in sorted_dates],
        'commit_counts': sorted_counts
    }

    cache.set(cache_key, render_object, timeout=60*5)

    return render(request, 'repository/insights/repository_insights.html', render_object)

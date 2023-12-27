from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from apps.branch.models import Branch
from apps.history.models import HistoryType, ChangeAction
from apps.pull_request.forms import PullRequestForm
from apps.pull_request.models import PullRequestStatus, PullRequest
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def pull_requests_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    pr_open = repository.pull_requests.filter(status=PullRequestStatus.OPEN.value)
    pr_merged = repository.pull_requests.filter(status=PullRequestStatus.MERGED.value)
    pr_closed = repository.pull_requests.filter(status=PullRequestStatus.CLOSED.value)

    render_object = {
        'repository': repository,
        'pr_open': pr_open,
        'pr_merged': pr_merged,
        'pr_closed': pr_closed
    }

    return render(request, 'repository/pull_requests/repository_pull_requests.html', render_object)


@login_required()
def add_pull_request(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})


@login_required()
def pull_request_detail(request, repository_id, pr_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    pull_request = get_object_or_404(PullRequest, pk=pr_id, repository=repository)
    render_object = {
        'repository': repository,
        'pull_request': pull_request
    }

    return render(request, 'repository/pull_requests/pull_request_details.html', render_object)


@login_required()
def add_pull_request(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = PullRequestForm(request.POST)

        if form.is_valid():
            pull_request = form.save(commit=False)
            pull_request.author = request.user
            pull_request.repository = repository
            pull_request.save()
            form.save_m2m()

            utils.create_history_item(
                user=request.user,
                history_type=HistoryType.REPOSITORY.value,
                changed_id=pull_request.id,
                changed_action=ChangeAction.OPENED.value,
                changed_name=pull_request.name
            )

            return redirect('repository_pull_requests', repository_id=repository.id)
        else:
            print(form.errors)
            form.fields['source'].queryset = Branch.objects.filter(repository=repository)
            form.fields['target'].queryset = Branch.objects.filter(repository=repository)
            form.fields['reviewers'].queryset = User.objects.filter(
                Q(repositories_collab=repository) | Q(id=repository.owner.id)
            ).exclude(id=request.user.id)

            error_message = 'Invalid form.'
            render_object = {
                'error_message': error_message,
                'form': form,
                'repository': repository
            }
            return render(request, 'repository/pull_requests/add_pull_request.html', render_object)
    else:
        form = PullRequestForm()
        form.fields['source'].queryset = Branch.objects.filter(repository=repository)
        form.fields['target'].queryset = Branch.objects.filter(repository=repository)
        form.fields['reviewers'].queryset = User.objects.filter(
            Q(repositories_collab=repository) | Q(id=repository.owner.id)
        ).exclude(id=request.user.id)

    return render(request, 'repository/pull_requests/add_pull_request.html', {'form': form, 'repository': repository})
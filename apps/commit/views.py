from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

import hashlib
import datetime

from apps.branch.models import Branch
from apps.commit.forms import CommitForm
from apps.history.models import HistoryType, ChangeAction
from mini_github import utils


@login_required()
def commits_from_branch(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    repository = branch.repository

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    commits = branch.commits.order_by('-date_time_created')
    render_object = {
        'repository': repository,
        'branch': branch,
        'commits': commits
    }

    return render(request, 'repository/commits/branch_commits.html', render_object)


@login_required()
def add_commit(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    repository = branch.repository

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = CommitForm(request.POST)
        if form.is_valid():
            commit = form.save(commit=False)
            commit.author = request.user
            commit.repository = repository

            hash_source = f"{commit.message}-{commit.repository.name}-{datetime.datetime.now()}"
            commit_hash = hashlib.sha256(hash_source.encode()).hexdigest()
            commit.hash = commit_hash

            commit.save()
            commit.branches.add(branch)

            utils.create_history_item(
                repository=repository,
                user=request.user,
                history_type=HistoryType.COMMIT.value,
                changed_id=branch.id,
                changed_action=ChangeAction.CREATED.value,
                changed_name=branch.name
            )

            return redirect('branch_commits', branch_id=branch.id)
        else:
            render_object = {
                'error_message': 'Invalid form.',
                'form': form,
                'repository': repository,
                'branch': branch
            }
            return render(request, 'repository/commits/add_commit.html', render_object)
    else:
        form = CommitForm()

    return render(request, 'repository/commits/add_commit.html', {
        'form': form,
        'repository': repository,
        'branch': branch
    })

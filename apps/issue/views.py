from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.history.models import HistoryType, ChangeAction
from apps.issue.forms import IssueForm
from apps.issue.models import Issue, ISSUE_STATUS, IssueStatus
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def issues_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issues = repository.issues.all().order_by('closed', '-date_created')
    render_object = {
        'repository': repository,
        'issues': issues
    }

    return render(request, 'repository/issues/repository_issues.html', render_object)


@login_required()
def issue_detail(request, repository_id, issue_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issue = get_object_or_404(Issue, pk=issue_id, repository=repository)

    return render(request, 'repository/issues/issue_details.html', {'repository': repository, 'issue': issue})


@login_required()
def add_issue(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = IssueForm(request.POST)

        if form.is_valid():
            issue = form.save(commit=False)
            issue.repository = repository
            issue.author = request.user

            project = form.cleaned_data.get('project')
            milestone = form.cleaned_data.get('milestone')
            assignees = form.cleaned_data.get('assignees')
            labels = form.cleaned_data.get('labels')

            if project and project.repository != repository:
                error_message = 'Selected project is not linked to this repository.'
                return issue_error(request, error_message, form, repository)

            if milestone and milestone.repository != repository:
                error_message = 'Selected milestone is not linked to this repository.'
                return issue_error(request, error_message, form, repository)

            if assignees and not all(assignee in repository.collaborators.all() for assignee in assignees):
                error_message = 'One or more selected assignees are not collaborators of this repository.'
                return issue_error(request, error_message, form, repository)

            if labels and not all(label in repository.labels.all() for label in labels):
                error_message = 'One or more selected labels are not linked to this repository.'
                return issue_error(request, error_message, form, repository)

            issue.save()
            form.save_m2m()

            utils.create_history_item(
                repository=repository,
                user=request.user,
                history_type=HistoryType.ISSUE.value,
                changed_id=issue.id,
                changed_action=ChangeAction.OPENED.value,
                changed_name=issue.name
            )

            return redirect('repository_issues', repository_id=repository.id)
        else:
            error_message = 'Invalid form'
            render_object = {
                'error_message': error_message,
                'repository': repository
            }
            return render(request, 'repository/issues/add_issue.html', render_object)
    else:
        form = IssueForm()

    return render(request, 'repository/issues/add_issue.html', {'form': form, 'repository': repository})


@login_required()
def close_issue(request, repository_id, issue_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issue = get_object_or_404(Issue, pk=issue_id, repository=repository)
    issue.change_closed()

    if issue.closed:
        utils.create_history_item(
            repository=repository,
            user=request.user,
            history_type=HistoryType.ISSUE.value,
            changed_id=issue.id,
            changed_action=ChangeAction.CLOSED.value,
            changed_name=issue.name
        )
    else:
        utils.create_history_item(
            repository=repository,
            user=request.user,
            history_type=HistoryType.ISSUE.value,
            changed_id=issue.id,
            changed_action=ChangeAction.OPENED.value,
            changed_name=issue.name
        )

    return redirect('issue_detail', repository_id=repository.id, issue_id=issue.id)


@login_required()
def edit_issue(request, repository_id, issue_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issue = get_object_or_404(Issue, id=issue_id, repository=repository)
    if request.method == 'POST':
        form = IssueForm(request.POST, instance=issue)

        if form.is_valid():
            form.save()
            return redirect('repository_issues', repository_id=repository.id)
        else:
            error_message = 'Invalid form'
            return render(request, 'repository/issues/edit_issue.html', {
                'error_message': error_message,
                'form': form,
                'issue': issue,
                'repository': repository
            })
    else:
        form = IssueForm(instance=issue)

    return render(request, 'repository/issues/edit_issue.html', {
        'form': form,
        'repository': repository,
        'issue': issue,
        'ISSUE_STATUS': ISSUE_STATUS
    })


@login_required()
def delete_issue(request, repository_id, issue_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issue = get_object_or_404(Issue, pk=issue_id, repository=repository)

    utils.create_history_item(
        repository=repository,
        user=request.user,
        history_type=HistoryType.ISSUE.value,
        changed_id=issue.id,
        changed_action=ChangeAction.DELETED.value,
        changed_name=issue.name
    )
    issue.delete()

    return redirect('repository_issues', repository_id=repository.id)


@login_required()
def move_issue_to_todo(request, repository_id, issue_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issue = get_object_or_404(Issue, pk=issue_id, repository_id=repository_id)
    issue.change_status(IssueStatus.TODO.name)

    return redirect('project_detail', repository_id=repository_id, project_id=issue.project.id)


@login_required()
def move_issue_to_in_progress(request, repository_id, issue_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issue = get_object_or_404(Issue, pk=issue_id, repository_id=repository_id)
    issue.change_status(IssueStatus.IN_PROGRESS.name)

    return redirect('project_detail', repository_id=repository_id, project_id=issue.project.id)


@login_required()
def move_issue_to_done(request, repository_id, issue_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issue = get_object_or_404(Issue, pk=issue_id, repository_id=repository_id)
    issue.change_status(IssueStatus.DONE.name)

    return redirect('project_detail', repository_id=repository_id, project_id=issue.project.id)


def issue_error(request, message, form, repository):
    render_object = {
        'error_message': message,
        'form': form,
        'repository': repository
    }
    return render(request, 'repository/issues/add_issue.html', render_object)

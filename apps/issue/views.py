from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.history.models import HistoryType, ChangeAction
from apps.issue.forms import IssueForm
from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def issues_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    issues = repository.issues.all().order_by('-date_created')
    render_object = {
        'repository': repository,
        'issues': issues
    }

    return render(request, 'repository/issues/repository_issues.html', render_object)


@login_required()
def issue_detail(request, repository_id, issue_id):
    pass


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

            project_id = form.cleaned_data.get('project')
            milestone_id = form.cleaned_data.get('milestone')

            if project_id and not Project.objects.filter(id=project_id, repository=repository).exists():
                error_message = 'Selected project is not linked to this repository.'
                return create_issue_error(request, error_message, form, repository)

            if milestone_id and not Milestone.objects.filter(id=milestone_id, repository=repository).exists():
                error_message = 'Selected milestone is not linked to this repository.'
                return create_issue_error(request, error_message, form, repository)

            # TODO check assignees and labels

            issue.save()
            form.save_m2m()

            utils.create_history_item(
                user=request.user,
                history_type=HistoryType.ISSUE.value,
                changed_id=issue.id,
                changed_action=ChangeAction.OPENED.value,
                changed_name=issue.name
            )

            return redirect('repository_issues', repository_id=repository.id)
        else:
            error_message = utils.get_error_message(form)
            render_object = {
                'error_message': error_message,
                'repository': repository
            }
            return render(request, 'repository/issues/add_issue.html', render_object)
    else:
        form = IssueForm()

    return render(request, 'repository/issues/add_issue.html', {'form': form, 'repository': repository})


def create_issue_error(request, message, form, repository):
    render_object = {
        'error_message': message,
        'form': form,
        'repository': repository
    }
    return render(request, 'repository/issues/add_issue.html', render_object)

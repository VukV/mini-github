from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.history.models import HistoryType, ChangeAction
from apps.issue.models import IssueStatus
from apps.project.forms import ProjectForm
from apps.project.models import Project
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def projects_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    projects = repository.projects.all()
    render_object = {
        'repository': repository,
        'projects': projects
    }

    return render(request, 'repository/projects/repository_projects.html', render_object)


@login_required()
def project_detail(request, repository_id, project_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    project = get_object_or_404(Project, pk=project_id, repository=repository)
    todo_issues = project.issues.filter(status=IssueStatus.TODO.name)
    in_progress_issues = project.issues.filter(status=IssueStatus.IN_PROGRESS.name)
    done_issues = project.issues.filter(status=IssueStatus.DONE.name)

    render_object = {
        'repository': repository,
        'project': project,
        'todo_issues': todo_issues,
        'in_progress_issues': in_progress_issues,
        'done_issues': done_issues
    }

    return render(request, 'repository/projects/project_details.html', render_object)


@login_required()
def add_project(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.repository = repository
            project.save()

            utils.create_history_item(
                repository=repository,
                user=request.user,
                history_type=HistoryType.PROJECT.value,
                changed_id=project.id,
                changed_action=ChangeAction.CREATED.value,
                changed_name=project.name
            )

            return redirect('repository_projects', repository_id=repository.id)
        else:
            error_message = utils.get_error_message(form)
            render_object = {
                'error_message': error_message,
                'repository': repository
            }
            return render(request, 'repository/projects/add_project.html', render_object)
    else:
        form = ProjectForm()

    return render(request, 'repository/projects/add_project.html', {'form': form, 'repository': repository})


@login_required()
def edit_project(request, repository_id, project_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    project = get_object_or_404(Project, id=project_id, repository=repository)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect('project_detail', repository_id=repository.id, project_id=project_id)
        else:
            error_message = 'Invalid form'
            return render(request, 'repository/projects/edit_project.html', {
                'error_message': error_message,
                'form': form,
                'project': project,
                'repository': repository
            })
    else:
        form = ProjectForm(instance=project)

    return render(request, 'repository/projects/edit_project.html', {
        'form': form,
        'project': project,
        'repository': repository
    })


@login_required()
def delete_project(request, repository_id, project_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    project = get_object_or_404(Project, pk=project_id, repository=repository)

    utils.create_history_item(
        repository=repository,
        user=request.user,
        history_type=HistoryType.PROJECT.value,
        changed_id=project.id,
        changed_action=ChangeAction.DELETED.value,
        changed_name=project.name
    )
    project.delete()

    return redirect('repository_projects', repository_id=repository.id)

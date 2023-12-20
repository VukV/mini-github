from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.branch.forms import BranchForm
from apps.branch.models import Branch
from apps.history.models import HistoryType, ChangeAction
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def branches_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    branches = repository.branches.order_by('-default')
    render_object = {
        'repository': repository,
        'branches': branches
    }

    return render(request, 'repository/branches/repository_branches.html', render_object)


@login_required()
def add_branch(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = BranchForm(request.POST)

        if form.is_valid():
            branch = form.save(commit=False)
            branch.repository = repository
            branch.save()

            utils.create_history_item(
                user=request.user,
                history_type=HistoryType.BRANCH.value,
                changed_id=branch.id,
                changed_action=ChangeAction.CREATED.value,
                changed_name=branch.name
            )

            return redirect('repository_branches', repository_id=repository.id)
        else:
            error_message = 'Invalid form.'
            render_object = {
                'error_message': error_message,
                'form': form,
                'repository': repository
            }
            return render(request, 'repository/branches/add_branch.html', render_object)
    else:
        form = BranchForm()

    return render(request, 'repository/branches/add_branch.html', {'form': form, 'repository': repository})


@login_required()
def edit_branch(request, repository_id, branch_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    branch = get_object_or_404(Branch, id=branch_id, repository=repository)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)

        if form.is_valid():
            form.save()
            return redirect('repository_branches', repository_id=repository.id)
        else:
            error_message = 'Invalid form'
            return render(request, 'repository/branches/edit_branch.html', {
                'error_message': error_message,
                'form': form,
                'repository': repository
            })
    else:
        form = BranchForm(instance=branch)

    return render(request, 'repository/branches/edit_branch.html', {'form': form, 'repository': repository})


@login_required()
def delete_branch(request, repository_id, branch_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    branch = get_object_or_404(Branch, pk=branch_id, repository=repository)

    if branch.default:
        error_message = 'You can not delete a default branch.'
        return render(request, 'error.html', {'error_message': error_message})

    utils.create_history_item(
        user=request.user,
        history_type=HistoryType.BRANCH.value,
        changed_id=branch.id,
        changed_action=ChangeAction.DELETED.value,
        changed_name=branch.name
    )
    branch.delete()

    return redirect('repository_branches', repository_id=repository_id)

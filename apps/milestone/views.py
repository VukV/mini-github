from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.history.models import HistoryType, ChangeAction
from apps.milestone.forms import MilestoneForm
from apps.milestone.models import Milestone
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def milestones_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    milestones = repository.milestones.all()
    render_object = {
        'repository': repository,
        'milestones': milestones
    }

    return render(request, 'repository/milestones/repository_milestones.html', render_object)


@login_required()
def add_milestone(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = MilestoneForm(request.POST)

        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.repository = repository
            milestone.save()

            utils.create_history_item(
                repository=repository,
                user=request.user,
                history_type=HistoryType.MILESTONE.value,
                changed_id=milestone.id,
                changed_action=ChangeAction.CREATED.value,
                changed_name=milestone.name
            )

            return redirect('repository_milestones', repository_id=repository.id)
        else:
            error_message = 'Invalid form.'
            render_object = {
                'error_message': error_message,
                'form': form,
                'repository': repository
            }
            return render(request, 'repository/milestones/add_milestone.html', render_object)
    else:
        form = MilestoneForm()

    return render(request, 'repository/milestones/add_milestone.html', {'form': form, 'repository': repository})


@login_required()
def edit_milestone(request, repository_id, milestone_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    milestone = get_object_or_404(Milestone, id=milestone_id, repository=repository)
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)

        if form.is_valid():
            form.save()
            return redirect('repository_milestones', repository_id=repository.id)
        else:
            error_message = 'Invalid form'
            return render(request, 'repository/milestones/edit_milestone.html', {
                'error_message': error_message,
                'form': form,
                'repository': repository
            })
    else:
        form = MilestoneForm(instance=milestone)

    return render(request, 'repository/milestones/edit_milestone.html', {'form': form, 'repository': repository})


@login_required()
def close_milestone(request, repository_id, milestone_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    milestone = get_object_or_404(Milestone, pk=milestone_id, repository=repository)
    if milestone.closed:
        milestone.set_closed(False)
        utils.create_history_item(
            repository=repository,
            user=request.user,
            history_type=HistoryType.MILESTONE.value,
            changed_id=milestone.id,
            changed_action=ChangeAction.OPENED.value,
            changed_name=milestone.name
        )
    else:
        milestone.set_closed(True)
        utils.create_history_item(
            repository=repository,
            user=request.user,
            history_type=HistoryType.MILESTONE.value,
            changed_id=milestone.id,
            changed_action=ChangeAction.CLOSED.value,
            changed_name=milestone.name
        )

    return redirect('repository_milestones', repository_id=repository_id)


@login_required()
def delete_milestone(request, repository_id, milestone_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    milestone = get_object_or_404(Milestone, pk=milestone_id, repository=repository)

    utils.create_history_item(
        repository=repository,
        user=request.user,
        history_type=HistoryType.MILESTONE.value,
        changed_id=milestone.id,
        changed_action=ChangeAction.DELETED.value,
        changed_name=milestone.name
    )
    milestone.delete()

    return redirect('repository_milestones', repository_id=repository_id)

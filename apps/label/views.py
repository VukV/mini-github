from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.history.models import HistoryType, ChangeAction
from apps.label.forms import LabelForm
from apps.label.models import Label
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def labels_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    labels = repository.labels.all()
    render_object = {
        'repository': repository,
        'labels': labels
    }

    return render(request, 'repository/labels/repository_labels.html', render_object)


@login_required()
def add_label(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = LabelForm(request.POST)

        if form.is_valid():
            label = form.save(commit=False)
            label.repository = repository
            label.save()

            utils.create_history_item(
                repository=repository,
                user=request.user,
                history_type=HistoryType.LABEL.value,
                changed_id=label.id,
                changed_action=ChangeAction.CREATED.value,
                changed_name=label.name
            )

            return redirect('repository_labels', repository_id=repository.id)
        else:
            error_message = utils.get_error_message(form)
            render_object = {
                'error_message': error_message,
                'repository': repository
            }
            return render(request, 'repository/labels/add_label.html', render_object)
    else:
        form = LabelForm()

    return render(request, 'repository/labels/add_label.html', {'form': form, 'repository': repository})


@login_required()
def edit_label(request, repository_id, label_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    label = get_object_or_404(Label, id=label_id, repository=repository)

    if request.method == 'POST':
        form = LabelForm(request.POST, instance=label)

        if form.is_valid():
            form.save()
            return redirect('repository_labels', repository_id=repository.id)
    else:
        form = LabelForm(instance=label)

    return render(request, 'repository/labels/edit_label.html', {'form': form, 'repository': repository})


@login_required()
def delete_label(request, repository_id, label_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    label = get_object_or_404(Label, pk=label_id, repository=repository)

    if label.issues.exists():
        error_message = 'Label is in use by issue(s).'
        return redirect_on_delete(request, error_message, repository)

    if label.pull_requests.exists():
        error_message = 'Label is in use by pull request(s).'
        return redirect_on_delete(request, error_message, repository)

    utils.create_history_item(
        repository=repository,
        user=request.user,
        history_type=HistoryType.LABEL.value,
        changed_id=label.id,
        changed_action=ChangeAction.DELETED.value,
        changed_name=label.name
    )
    label.delete()

    return redirect('repository_labels', repository_id=repository.id)


def redirect_on_delete(request, message, repository):
    render_object = {
        'error_message': message,
        'repository': repository
    }
    return render(request, 'repository/labels/repository_labels.html', render_object)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from apps.repository.models import Repository


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

    return render(request, 'repository/repository_labels.html', render_object)


@login_required()
def add_label(request, repository_id):
    # Logic to handle adding a new label
    pass


@login_required()
def edit_label(request, repository_id, label_id):
    # Logic to handle label editing
    pass


@login_required()
def delete_label(request, repository_id, label_id):
    # Logic to handle label deletion
    pass

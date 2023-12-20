from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from apps.repository.models import Repository


@login_required()
def branches_from_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    branches = repository.branches.all()
    render_object = {
        'repository': repository,
        'branches': branches
    }

    return render(request, 'repository/branches/repository_branches.html', render_object)

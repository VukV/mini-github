from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.history.models import ChangeAction, HistoryType
from apps.repository.forms import RepositoryForm
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def repository_detail(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'repository/repository.html', {'error_message': error_message})

    return render(request, 'repository/repository.html', {'repository': repository})


@login_required()
def create_repository(request):
    if request.method == 'POST':
        form = RepositoryForm(request.POST)

        if form.is_valid():
            repository = form.save(commit=False)
            repository.owner = request.user
            repository.save()
            form.save_m2m()  # required for saving many-to-many relationships

            utils.create_history_item(
                user=request.user,
                history_type=HistoryType.REPOSITORY.value,
                changed_id=repository.id,
                changed_action=ChangeAction.CREATED.value,
                changed_name=repository.name
            )

            return redirect('repository', repository_id=repository.id)
        else:
            error_message = utils.get_error_message(form)
            return render(request, 'repository/repository_create.html', {'error_message': error_message})
    else:
        form = RepositoryForm()

    return render(request, 'repository/repository_create.html', {'form': form})

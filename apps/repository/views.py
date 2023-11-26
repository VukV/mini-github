from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.repository.forms import RepositoryForm
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def repository_detail(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)
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

            return redirect('dashboard')
        else:
            error_message = utils.get_error_message(form)
            return render(request, 'repository/repository_create.html', {'error_message': error_message})
    else:
        form = RepositoryForm()

    return render(request, 'repository/repository_create.html', {'form': form})

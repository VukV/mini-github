import hashlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

from apps.branch.models import Branch
from apps.commit.models import Commit
from apps.history.models import ChangeAction, HistoryType
from apps.repository.forms import RepositoryForm
from apps.repository.models import Repository
from mini_github import utils


@login_required()
def repository_detail(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    return render(request, 'repository/repository.html', {'repository': repository})


@login_required()
def create_repository(request):
    if request.method == 'POST':
        form = RepositoryForm(request.POST)

        if form.is_valid():
            repository = form.save(commit=False)
            repository.owner = request.user
            repository.save()

            repository.collaborators.add(request.user)
            form.save_m2m()

            main_branch = Branch(name='main', default=True, repository=repository)
            main_branch.save()

            utils.create_history_item(
                repository=repository,
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


@login_required()
def repository_settings(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if repository.owner != request.user:
        error_message = 'You do not have access to repository settings.'
        return render(request, 'error.html', {'error_message': error_message})

    collaborators = repository.collaborators.exclude(id=repository.owner.id)

    render_object = {
        'repository': repository,
        'collaborators': collaborators,
    }

    return render(request, 'repository/repository_settings.html', render_object)


@login_required()
def delete_repository(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)

    if request.user != repository.owner:
        error_message = 'You do not have permission to delete this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    utils.create_history_item(
        repository=repository,
        user=request.user,
        history_type=HistoryType.REPOSITORY.value,
        changed_id=repository.id,
        changed_action=ChangeAction.DELETED.value,
        changed_name=repository.name
    )
    repository.delete()

    return redirect('dashboard')


@login_required()
def change_repository_visibility(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if request.user != repository.owner:
        error_message = 'You do not have permission to change visibility.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        visibility = request.POST.get('visibility') == 'public'
        repository.public = visibility
        repository.save()

    return redirect('repository_settings', repository_id=repository_id)


@login_required()
def rename_repository(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if request.user != repository.owner:
        error_message = 'You do not have permission to change repository name.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        new_name = request.POST.get('name')
        repository.name = new_name
        repository.save()

    return redirect('repository_settings', repository_id=repository_id)


@login_required()
def add_collaborator(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if request.user != repository.owner:
        error_message = 'You do not have permission to add collaborators.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            repository.collaborators.add(user)
        except User.DoesNotExist:
            error_message = 'User does not exist.'
            messages.error(request, error_message)

    return redirect('repository_settings', repository_id=repository_id)


@login_required()
def remove_collaborator(request, repository_id, user_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if request.user != repository.owner:
        error_message = 'You do not have permission to remove collaborators.'
        return render(request, 'error.html', {'error_message': error_message})

    if user_id == repository.owner:
        error_message = 'Can not remove repository owner.'
        return render(request, 'error.html', {'error_message': error_message})

    try:
        user = User.objects.get(id=user_id)
        repository.collaborators.remove(user)
    except User.DoesNotExist:
        error_message = 'User does not exist.'
        messages.error(request, error_message)

    return redirect('repository_settings', repository_id=repository_id)


@login_required()
def repository_star(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.user in repository.stars.all():
        repository.stars.remove(request.user)
    else:
        repository.stars.add(request.user)

    return redirect('repository', repository_id=repository_id)


@login_required()
def repository_watch(request, repository_id):
    repository = get_object_or_404(Repository, id=repository_id)

    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.user in repository.watchers.all():
        repository.watchers.remove(request.user)
    else:
        repository.watchers.add(request.user)

    return redirect('repository', repository_id=repository_id)


@login_required()
def repository_fork(request, repository_id):
    original_repository = get_object_or_404(Repository, id=repository_id)

    if not original_repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    with transaction.atomic():
        forked_repository = Repository.objects.create(
            name=f"{original_repository.name} (forked)",
            public=original_repository.public,
            owner=request.user
        )

        for branch in original_repository.branches.all():
            forked_branch = Branch.objects.create(
                name=branch.name,
                default=branch.default,
                repository=forked_repository
            )

            for commit in branch.commits.all():
                hash_source = f"{commit.message}-{commit.repository.name}-{commit.date_time_created}-fork"
                new_commit_hash = hashlib.sha256(hash_source.encode()).hexdigest()
                Commit.objects.create(
                    hash=new_commit_hash,
                    message=commit.message,
                    date_time_created=commit.date_time_created,
                    author=commit.author,
                    repository=forked_repository
                ).branches.add(forked_branch)

        return redirect('repository', repository_id=forked_repository.id)

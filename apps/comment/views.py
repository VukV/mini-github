from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.comment.forms import CommentForm
from apps.comment.models import Comment
from apps.pull_request.models import PullRequest


@login_required()
def add_comment(request, pr_id):
    pull_request = get_object_or_404(PullRequest, pk=pr_id)

    repository = pull_request.repository
    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        comment_text = request.POST.get('text')

        if comment_text:
            Comment.objects.create(
                author=request.user,
                text=comment_text,
                pull_request=pull_request
            )
        else:
            error_message = 'Comment text is required.'
            return render(request, 'error.html', {'error_message': error_message})

        return redirect('pull_request_detail', repository_id=repository.id, pr_id=pull_request.id)

    return redirect('pull_request_detail', repository_id=repository.id, pr_id=pull_request.id)


@login_required()
def reply_comment(request, pr_id, comment_id):
    pull_request = get_object_or_404(PullRequest, pk=pr_id)

    repository = pull_request.repository
    if not repository.check_access(request.user):
        error_message = 'You do not have access to this repository.'
        return render(request, 'error.html', {'error_message': error_message})

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            replied_to_id = request.POST.get('replied_to')
            parent_comment = get_object_or_404(Comment, pk=replied_to_id)

            reply = form.save(commit=False)
            reply.author = request.user
            reply.pull_request = pull_request
            reply.replied_to = parent_comment

            reply.save()
        else:
            error_message = 'Invalid reply.'
            return render(request, 'error.html', {'error_message': error_message})

        return redirect('pull_request_detail', repository_id=repository.id, pr_id=pull_request.id)
from django.utils import timezone

from apps.history.models import History


def get_error_message(form):
    error = next(iter(form.errors.as_data().values()))[0]
    try:
        if isinstance(error.params, dict):
            error_message = error.message % error.params
        else:
            error_message = error.message
    except TypeError:
        error_message = error.message

    return error_message


def create_history_item(repository, user, history_type, changed_id, changed_action, changed_name):
    History.objects.create(
        repository=repository,
        user_changed=user,
        date_time_changed=timezone.now(),
        type=history_type,
        changed_id=changed_id,
        changed_action=changed_action,
        changed_name=changed_name
    )

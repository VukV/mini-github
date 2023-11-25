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

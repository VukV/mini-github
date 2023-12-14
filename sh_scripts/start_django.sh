#!/bin/bash

# collect static files
python manage.py collectstatic --noinput

# apply database migrations
python manage.py migrate

# start the Django application using Gunicorn on port 8001
gunicorn mini_github.wsgi:application --bind 0.0.0.0:8001

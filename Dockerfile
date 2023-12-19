# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create a directory for the app
RUN mkdir /app

# Set the working directory in the container to /app
WORKDIR /app

# Install psycopg2 dependencies
RUN apt-get update \
  && apt-get install -y postgresql gcc python3-dev musl-dev \
  && apt-get clean

# Upgrade pip and install wheel and setuptools
RUN pip install --upgrade pip wheel setuptools

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make scripts executable
RUN chmod +x /app/sh_scripts/database_wait.sh
RUN chmod +x /app/sh_scripts/start_django.sh

# Execute the wait_for_db.sh script when the container launches which in turn calls start.sh to run the Django app
CMD ["/app/sh_scripts/database_wait.sh"]

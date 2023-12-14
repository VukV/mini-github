FROM nginx:latest

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy the configuration file from the current directory to the container
COPY default.conf /etc/nginx/conf.d/

# Expose port 80 to the Docker host, so we can access it
# from the outside.
EXPOSE 80

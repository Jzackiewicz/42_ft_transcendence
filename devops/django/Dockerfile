# Dockerfile Reference: https://docs.docker.com/engine/reference/builder/
# Python Base Image: https://hub.docker.com/_/python
# Django Deployment Guide: https://docs.djangoproject.com/en/5.0/howto/deployment/
# Daphne ASGI Server: https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/daphne/

FROM python:3.13.1-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY server/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY server/ /app/
COPY devops/django/entrypoint.sh /usr/local/bin/


# Set permissions
RUN chmod +x /usr/local/bin/entrypoint.sh

# Entrypoint and default command
ENTRYPOINT ["entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]

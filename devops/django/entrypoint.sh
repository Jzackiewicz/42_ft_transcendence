#!/bin/sh

# Shell scripting basics: https://linuxconfig.org/bash-scripting-tutorial-for-beginners
# Wait-for-DB pattern: https://docs.docker.com/compose/startup-order/
# Django Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/

set -e

echo "Waiting for database..."
MAX_RETRIES=10
COUNT=0
until python manage.py check --database default >/dev/null 2>&1 || [ $COUNT -eq $MAX_RETRIES ]; do
	sleep 2
	COUNT=$((COUNT + 1))
	echo "Retry $COUNT/$MAX_RETRIES..."
done

if [ $COUNT -eq $MAX_RETRIES ]; then
	echo "Database connection failed after $MAX_RETRIES attempts."
	exit 1
fi

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the main command (Daphne)
exec "$@"

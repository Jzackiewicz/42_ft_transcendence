#!/bin/bash
set -e

cd server/
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install -r requirements.txt

# Remove the database if it exists before migrating
rm -f db.sqlite3

python3 manage.py makemigrations
python3 manage.py migrate


DJANGO_SUPERUSER_PASSWORD=admin python3 manage.py createsuperuser \
    --noinput \
    --username=admin \
    --email=admin@example.com || true

python3 manage.py runserver
#!/bin/sh
set -e

cd /app
python manage.py collectstatic --noinput || true
python manage.py migrate --noinput || true
exec python -m gunicorn --bind 0.0.0.0:8000 --workers 3 hexalearn.wsgi:application
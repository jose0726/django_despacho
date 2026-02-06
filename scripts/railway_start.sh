#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Run migrations and collect static assets on deploy/start.
python despacho_django/manage.py migrate --noinput
python despacho_django/manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn despacho_django.wsgi:application --chdir despacho_django --bind 0.0.0.0:"${PORT:-8080}" --workers "${WEB_CONCURRENCY:-2}" --timeout "${GUNICORN_TIMEOUT:-60}"

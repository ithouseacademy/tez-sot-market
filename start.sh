#!/bin/bash
echo "=== Running migrations ==="
python manage.py migrate --noinput 2>&1
echo "=== Starting gunicorn ==="
gunicorn beckend.wsgi:application --bind 0.0.0.0:$PORT --workers 4 2>&1

#!/bin/sh
python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input
gunicorn rest_api.wsgi:application --bind 0.0.0.0:8084 -D
nginx
gunicorn rest_api.wsgi:application --bind 0.0.0.0:8081

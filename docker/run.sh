#!/bin/bash
set -eux
python manage.py migrate --noinput
gunicorn blog.wsgi -b 0.0.0.0:8000 --log-file -

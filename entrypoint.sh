#!/bin/bash
set -e

if [ "$1" = "run" ]; then
  if [ "$DEBUG" != 'True' ] && [ "$DEBUG" != 'true' ]; then
      python manage.py collectstatic -v 2 --noinput --no-color
  else
      export PYTHONDONTWRITEBYTECODE=1
  fi

  # Migrations
  python manage.py migrate --no-color --no-input --verbosity 2

  if [ "$DEBUG" = 'True' ] || [ "$DEBUG" = 'true' ]; then
      exec python manage.py runserver 0.0.0.0:8000
  else
      exec gunicorn "lottery_api.wsgi:application" \
          --bind 0.0.0.0:$PORT
  fi
elif [ "$1" = "test" ]; then
    python3 -m pytest \
        --junitxml=unit_test_results.xml \
        --cov && \
    coverage xml
else
    echo "Command not found '$1'"
    exit 1
fi
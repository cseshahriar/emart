#!/bin/sh

set -e  # Exit immediately if any command fails

echo "Waiting for PostgreSQL..."

# Wait until DB is ready
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - continuing"

# Apply migrations and collect static files
echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000

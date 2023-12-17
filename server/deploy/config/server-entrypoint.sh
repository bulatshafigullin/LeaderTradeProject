#!/bin/sh

# Until server folder created
until cd /app/server; do
  echo "Waiting for server volume..."
done

until python manage.py makemigrations base users profiles locations catalog interface products billing orders actions unloads news; do
  echo "Waiting for db to be ready..."
  sleep 2
done

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py createsettings

python manage.py createadmin

python manage.py createcategory

python manage.py createintervals

echo "Start LeaderTrade Server..."

gunicorn core.wsgi:application --bind 0.0.0.0:8100

exec "$@"
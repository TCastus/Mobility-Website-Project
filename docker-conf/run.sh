#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
	echo "Waiting for postgres..."

	while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
		sleep 0.1
	done

	echo "PostgreSQL started"
fi

python3 manage.py migrate
python3 manage.py collectstatic --no-input --clear

uwsgi --module=mobility.wsgi:application --http=0.0.0.0:8000 --threads=4 --processes=1

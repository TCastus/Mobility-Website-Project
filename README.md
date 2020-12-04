# International mobility website - Astus International

## Installation
2 possibilities for installation: Virtualenv + dockerized db, or Docker-compose. docker-compose uwsgi launch doesn't have file watchers and is meant for production-like environment.

1) Virtualenv + dockerized postgres
Best for local development. Depends on : virtualenv (installed via pip), Docker
```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
docker run --rm --name db_mobility -it -v db_mobility:/var/lib/postgresql/data -p 5432:5432 -e POSTGRES_USER=user -e POSTGRES_DB=db -e POSTGRES_PASSWORD=password postgres
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver
```

2) Docker-compose
Doesn't use `.env` file. Depends on : Docker, docker-compose
```shell
docker-compose up

# Access a container using docker exec
docker exec -it mobility-django python manage.py createsuperuser
```

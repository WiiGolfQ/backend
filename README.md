# WiiGolfQ/backend

This repository contains WiiGolfQ's backend implementation. It is written in [Django](https://www.djangoproject.com/) and uses [Django REST Framework](https://www.django-rest-framework.org/) for its REST API. It uses [PostgreSQL](https://www.postgresql.org/) as its choice of SQL database.

#### Features

- Matchmaking
- Rating system using [OpenSkill](https://openskill.me/en/stable/)
- Leaderboards for player ratings and individual score performances
- REST API

## Running locally

### Install PostgreSQL

- [Install PostgreSQL.](https://www.postgresql.org/download/)
- Create a new database and user.

```
su - postgres
createuser wgquser
createdb wgqdb
psql
# enter postgres password (`postgres` by default)
alter user wgquser with encrypted password 'InsertPasswordHere';
grant all privileges on database wgqdb to wgquser;
```

### Cloning and changing environment variables

```
git clone git@github.com:wiigolfq/backend
cd backend

cp .env.example .env
nano .env  #change environment variables, see below
```

#### Environment variables

- `DJANGO_SECRET`
  - [A secret key for Django. Should be a long, random string.](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-SECRET_KEY)
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
  - Postgres credentials you just made.
- `POSTGRES_HOST`
  - The database should be at `[POSTGRES_HOST]:5432`. Defaults to `localhost` if `DEBUG` is `true`.
- `DEBUG`
  - Leave `false` in production.
 
## Running

```
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python3 manage.py migrate

python3 manage.py createsuperuser
# follow on-screen instructions

python3 manage.py runserver
```

The backend should now be up at `localhost:8000`. Visit http://localhost:8000/admin to log into the admin panel with the superuser credentials you created.



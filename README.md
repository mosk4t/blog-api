# Blog API — Homework 1

A Django REST API with a custom email-based user, JWT authentication, posts,
comments, categories and tags. Built for Homework 1, ready to extend in Homework 2.

## Entity Relationship Diagram

![ERD](docs/erd.svg)

Relationships: User 1:N Post; User 1:N Comment; Category 1:N Post
(optional); Post 1:N Comment; Post N:M Tag.

## Requirements

Python 3.11+ and pip. Local environment uses SQLite; production uses PostgreSQL.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements/dev.txt
# Windows PowerShell: Copy-Item settings/.env.example settings/.env
# macOS/Linux: cp settings/.env.example settings/.env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin at http://127.0.0.1:8000/admin/.

`settings/.env` is ignored by Git. Set `BLOG_ENV_ID=local` for SQLite. For
production, set `BLOG_ENV_ID=prod` and configure `BLOG_DB_*` for PostgreSQL.
All configuration variables are prefixed `BLOG_`.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register using email/password/name |
| POST | `/api/auth/token/` | JWT access and refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh JWT |
| GET | `/api/auth/me/` | Current user profile |
| GET, POST | `/api/posts/` | Public published posts / create own post |
| GET, PUT, PATCH, DELETE | `/api/posts/{slug}/` | Post detail / owner edit |
| GET, POST | `/api/comments/` | Public comments / comment on published post |
| GET, POST | `/api/categories/`, `/api/tags/` | List / staff-only write |

Example token request:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"your-password"}'
```

Then send `Authorization: Bearer <access-token>` on protected calls.

## Git workflow

1. Create a **public** repository named `blog-api` on GitHub.
2. Work on `hw1`, then merge to `main` without deleting `hw1`.
3. Create `hw2` from `main`, merge back to `main` without deleting `hw2`.

If using the supplied local git repository, see the accompanying instructions.

## Code quality

`python -m ruff check .`, `python manage.py check`, `python manage.py test`,
`python manage.py makemigrations --check --dry-run`.

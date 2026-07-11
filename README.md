# Resume Builder API

An async **Django REST API** that generates PDF resumes from structured data. Built on **django-ninja** with **Pydantic** validation, renders resumes with **WeasyPrint** from an HTML template, and uploads the result to **S3-compatible storage** (async, via aioboto3). The API returns a public URL to the generated PDF.

## Features

- **Resumes**: create, list, retrieve, update (full and partial), delete.
- **PDF generation**: resume data is rendered into a styled HTML template and converted to PDF by WeasyPrint.
- **S3 storage**: generated PDFs are uploaded asynchronously to any S3-compatible storage; the public URL is stored with the resume.
- **Fully async**: async django-ninja handlers, async ORM access, async S3 uploads; the only sync piece (WeasyPrint rendering) is bridged with `sync_to_async`.
- **Typed schemas**: django-ninja `ModelSchema` with `*In` / `*Out` naming for request and response validation.
- **Repository layer**: a generic `Repository[T]` isolates all ORM queries, services stay focused on business logic.
- **API docs**: auto-generated OpenAPI schema and **Swagger UI**.
- **Env-driven config**: settings split into focused modules, secrets loaded via django-environ.

## Tech stack

| Layer    | Technologies                                                     |
|----------|------------------------------------------------------------------|
| API      | Django 6, django-ninja (Pydantic), async handlers, Uvicorn (ASGI) |
| PDF      | WeasyPrint (HTML template → PDF)                                 |
| Storage  | S3-compatible object storage via aioboto3, downloads via httpx   |
| Database | Any Django-supported DB in production; SQLite when `DEBUG=True`  |
| Config   | django-environ (`.env` file / environment variables)             |
| Tooling  | uv, Black                                                        |

## Application structure

```text
.
├── src/
│   ├── manage.py
│   ├── core/                      # Django project (settings, routing, ASGI)
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   ├── urls.py                # mounts /admin/ and /api/
│   │   ├── api.py                 # NinjaAPI factory, mounts resume router
│   │   ├── s3_client.py           # async S3 client (aioboto3 + httpx)
│   │   └── settings/
│   │       ├── env.py             # typed env vars declaration (django-environ)
│   │       ├── apps.py            # INSTALLED_APPS
│   │       ├── base.py            # core Django settings
│   │       ├── database.py        # sqlite (DEBUG) / env-configured DB switch
│   │       └── s3.py              # S3 storage configuration
│   └── resume/                    # Resume app
│       ├── migrations/
│       ├── templates/
│       │   └── main.html          # resume PDF template
│       ├── admin.py
│       ├── models.py              # Resume model
│       ├── repository.py          # generic async Repository[T]
│       ├── schemas.py             # ninja ModelSchema In/Out schemas
│       ├── service.py             # PDF build + S3 upload orchestration
│       └── views.py               # async ninja handlers
├── pyproject.toml
└── uv.lock
```

## Requirements

- **Python 3.14+**
- **[uv](https://docs.astral.sh/uv/)** for dependency management
- **S3-compatible storage** (e.g. Yandex Object Storage, MinIO, AWS S3) with a bucket for generated PDFs
- WeasyPrint system dependencies (Pango/Cairo); see the [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

## Configuration

Create a `.env` file next to `manage.py` (see `src/.env.example`; the file is gitignored — do not commit secrets):

| Variable                                                                                    | Purpose                                                            |
|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| `SECRET_KEY`                                                                                | Django secret key                                                  |
| `DEBUG`                                                                                     | `True` for local dev (SQLite); `False` for production              |
| `ALLOWED_HOSTS`                                                                             | Comma-separated list of allowed hosts                              |
| `DATABASE_ENGINE`, `DATABASE_NAME`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT` | Database credentials, used only when `DEBUG=False` |
| `S3_ENDPOINT_URL`                                                                           | S3-compatible storage endpoint                                     |
| `S3_REGION`                                                                                 | Storage region                                                     |
| `S3_ACCESS_KEY`, `S3_SECRET_KEY`                                                            | Storage credentials                                                |
| `S3_BUCKET_NAME`                                                                            | Bucket for generated PDF files                                     |

Minimal local `.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key

S3_REGION=ru-central1
S3_ENDPOINT_URL=https://storage.yandexcloud.net
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET_NAME=resume-builder
```

## Local development

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Apply migrations:
   ```bash
   cd src
   uv run python manage.py migrate
   ```

3. Start the API:
   ```bash
   uv run python manage.py runserver
   ```
   or via Uvicorn (production-style ASGI):
   ```bash
   uv run uvicorn core.asgi:application
   ```

With `DEBUG=True` the project uses SQLite — no external database required. S3 credentials are still needed to create resumes, since generated PDFs are uploaded on every create/update.

## API overview

Base URL prefix: `/api/`.

| Method          | Path                    | Description                                  |
|-----------------|-------------------------|----------------------------------------------|
| `POST`          | `/api/resume`           | Create a resume, returns the PDF URL          |
| `GET`           | `/api/resume`           | List URLs of all resumes                      |
| `GET`           | `/api/resume/{id}`      | Get the PDF URL of a resume                   |
| `PUT` / `PATCH` | `/api/resume/{id}`      | Update a resume, regenerates and reuploads PDF |
| `DELETE`        | `/api/delete/{id}`      | Delete a resume                               |

Request bodies are validated by the `ResumeIn` schema (`title`, `phone_number`, `email`, `experience`, `education`). Every create/update renders a fresh PDF, uploads it to S3 and responds with its public URL:

```json
{ "url": "https://storage.example.com/resume-builder/<key>.pdf" }
```

Interactive documentation:

- **Swagger UI**: `/api/docs`
- **OpenAPI schema**: `/api/openapi.json`

Django admin: `/admin/`

## Development tooling

- **Black**: `uv run black .`

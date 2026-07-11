"""
Environment variables (django-environ).
https://django-environ.readthedocs.io/
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, ""),
    ALLOWED_HOSTS=(list, []),

    DATABASE_ENGINE=(str, "django.db.backends.sqlite3"),
    DATABASE_NAME=(str, ""),
    DATABASE_USERNAME=(str, ""),
    DATABASE_PASSWORD=(str, ""),
    DATABASE_HOST=(str, ""),
    DATABASE_PORT=(str, ""),

    S3_REGION=(str, ""),
    S3_ENDPOINT_URL=(str, ""),
    S3_ACCESS_KEY=(str, ""),
    S3_SECRET_KEY=(str, ""),
    S3_BUCKET_NAME=(str, ""),
)

environ.Env.read_env(BASE_DIR / ".env")

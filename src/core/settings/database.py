"""
Database settings.
https://docs.djangoproject.com/en/6.0/ref/settings/#databases
"""

from .env import BASE_DIR, env

if env("DEBUG"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": env("DATABASE_ENGINE"),
            "NAME": env("DATABASE_NAME"),
            "USER": env("DATABASE_USERNAME"),
            "PASSWORD": env("DATABASE_PASSWORD"),
            "HOST": env("DATABASE_HOST"),
            "PORT": env("DATABASE_PORT"),
        }
    }

"""PostgreSQL setup for production."""

from settings.base import *  # noqa: F403,F401
from settings.conf import (
    BLOG_DB_HOST,
    BLOG_DB_NAME,
    BLOG_DB_PASSWORD,
    BLOG_DB_PORT,
    BLOG_DB_USER,
)

DEBUG = False
if SECRET_KEY == "unsafe-for-development-only":  # noqa: F405
    raise RuntimeError("Set BLOG_SECRET_KEY in production")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": BLOG_DB_NAME,
        "USER": BLOG_DB_USER,
        "PASSWORD": BLOG_DB_PASSWORD,
        "HOST": BLOG_DB_HOST,
        "PORT": BLOG_DB_PORT,
    }
}
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

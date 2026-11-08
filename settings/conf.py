"""Application configuration sourced from settings/.env (and environment)."""

from pathlib import Path

from decouple import AutoConfig

ROOT = Path(__file__).resolve().parent
config = AutoConfig(search_path=str(ROOT))

BLOG_ENV_ID = config("BLOG_ENV_ID", default="local")
BLOG_SECRET_KEY = config("BLOG_SECRET_KEY", default="unsafe-for-development-only")
BLOG_ALLOWED_HOSTS = config(
    "BLOG_ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=lambda x: x.split(",")
)
BLOG_DB_NAME = config("BLOG_DB_NAME", default="blog_api")
BLOG_DB_USER = config("BLOG_DB_USER", default="blog_user")
BLOG_DB_PASSWORD = config("BLOG_DB_PASSWORD", default="")
BLOG_DB_HOST = config("BLOG_DB_HOST", default="localhost")
BLOG_DB_PORT = config("BLOG_DB_PORT", default="5432")

#!/usr/bin/env python
"""Project management CLI, selecting settings from settings/.env."""

import os
import sys
from pathlib import Path


def main() -> None:
    from decouple import Config, RepositoryEnv

    env_path = Path(__file__).resolve().parent / "settings" / ".env"
    if env_path.exists():
        environment = Config(RepositoryEnv(str(env_path)))(
            "BLOG_ENV_ID", default="local"
        )
    else:
        environment = os.getenv("BLOG_ENV_ID", "local")
    if environment not in {"local", "prod"}:
        raise ValueError("BLOG_ENV_ID must be 'local' or 'prod'")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{environment}")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

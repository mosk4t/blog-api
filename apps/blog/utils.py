"""Pure-ish helpers for unique post slugs."""

from apps.blog.models import Post


def unique_post_slug(base: str, instance: Post | None = None) -> str:
    base = (base or "post")[:200]
    candidate = base
    number = 2
    used = Post.objects.exclude(pk=getattr(instance, "pk", None)).values_list(
        "slug", flat=True
    )
    existing = set(used)
    while candidate in existing:
        suffix = f"-{number}"
        candidate = f"{base[:220 - len(suffix)]}{suffix}"
        number += 1
    return candidate

"""Reusable Django Unfold navigation and dashboard callbacks."""

import json

from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post
from settings.conf import BLOG_ENV_ID

TOP_AUTHORS = 5
PERCENT = 100


def environment_badge(request: HttpRequest) -> list[str]:
    if BLOG_ENV_ID == "prod":
        return ["Production", "danger"]
    return ["Local", "warning"]


def draft_badge(request: HttpRequest) -> int:
    return Post.objects.filter(status=Post.Status.DRAFT).count()


def superuser_only(request: HttpRequest) -> bool:
    return request.user.is_superuser


def posts_all_tab(request: HttpRequest) -> str:
    return reverse("admin:blog_post_changelist")


def posts_published_tab(request: HttpRequest) -> str:
    return f'{reverse("admin:blog_post_changelist")}?status__exact=published'


def posts_draft_tab(request: HttpRequest) -> str:
    return f'{reverse("admin:blog_post_changelist")}?status__exact=draft'


def dashboard_callback(request: HttpRequest, context: dict) -> dict:
    total_users = User.objects.count()
    total_published = Post.objects.filter(status=Post.Status.PUBLISHED).count()
    total_drafts = Post.objects.filter(status=Post.Status.DRAFT).count()
    total_comments = Comment.objects.count()
    total_posts = total_published + total_drafts

    per_category = list(
        Category.objects.annotate(post_count=Count("posts"))
        .order_by("name")
        .values("name", "post_count")
    )
    authors = (
        User.objects.annotate(post_count=Count("posts"))
        .order_by("-post_count", "email")[:TOP_AUTHORS]
    )
    context.update(
        {
            "stat_cards": [
                {"label": "Total users", "value": total_users, "icon": "group"},
                {"label": "Published", "value": total_published, "icon": "check_circle"},
                {"label": "Drafts", "value": total_drafts, "icon": "edit_note"},
                {"label": "Comments", "value": total_comments, "icon": "chat"},
            ],
            "posts_chart": json.dumps(
                {
                    "labels": [entry["name"] for entry in per_category],
                    "datasets": [
                        {
                            "label": "Posts",
                            "data": [entry["post_count"] for entry in per_category],
                            "backgroundColor": "#0d9488",
                        }
                    ],
                }
            ),
            "top_authors": {
                "headers": ["Author", "Email", "Posts"],
                "rows": [
                    [author.get_full_name(), author.email, author.post_count]
                    for author in authors
                ],
            },
            "published_pct": (
                round(total_published / total_posts * PERCENT, 1)
                if total_posts else 0
            ),
            "draft_pct": (
                round(total_drafts / total_posts * PERCENT, 1)
                if total_posts else 0
            ),
        }
    )
    return context

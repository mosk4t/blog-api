"""Populate the blog database with realistic, repeat-safe demo data."""

import random
from time import perf_counter
from typing import Any

from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand, CommandError
from django.core.management.base import CommandParser
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post, Tag

DEFAULT_USERS = 20
DEFAULT_POSTS = 100
DEFAULT_COMMENTS = 500
SEED_PASSWORD = "DemoPassword2026!"
PUBLISHED_RATIO = 0.70
UNCATEGORIZED_RATIO = 0.10
INACTIVE_RATIO = 0.15
STAFF_RATIO = 0.10
MAX_TAGS_PER_POST = 5
MIN_PARAGRAPHS = 3
MAX_PARAGRAPHS = 5
MIN_COMMENT_SENTENCES = 1
MAX_COMMENT_SENTENCES = 3
POST_TITLE_WORDS = 7
FIRST_DUPLICATE_SUFFIX = 2

CATEGORY_NAMES = (
    "Python", "Django", "DevOps", "Data Science", "Web Development",
    "Cloud Computing", "Cybersecurity", "Machine Learning",
)
TAG_NAMES = (
    "tutorial", "beginner", "advanced", "api", "rest", "database",
    "postgresql", "sqlite", "docker", "deployment", "testing", "jwt",
    "security", "performance", "optimization", "frontend", "backend",
    "javascript", "automation", "open-source",
)


class Command(BaseCommand):
    help = "Fill the database with fake data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users", type=int, default=DEFAULT_USERS,
            help="Number of users to create",
        )
        parser.add_argument(
            "--posts", type=int, default=DEFAULT_POSTS,
            help="Number of posts to create",
        )
        parser.add_argument(
            "--comments", type=int, default=DEFAULT_COMMENTS,
            help="Number of comments to create",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="Clear existing data (preserving superusers) before seeding",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        started = perf_counter()
        user_count: int = options["users"]
        post_count: int = options["posts"]
        comment_count: int = options["comments"]

        for label, count in (
            ("users", user_count),
            ("posts", post_count),
            ("comments", comment_count),
        ):
            if count < 0:
                raise CommandError(f"--{label} must be zero or greater")

        if options["clear"]:
            self._clear()

        fake = Faker("en_US")
        users = self._create_users(fake, user_count)
        categories = self._create_named(Category, CATEGORY_NAMES)
        tags = self._create_named(Tag, TAG_NAMES)
        if (post_count or comment_count) and not users:
            raise CommandError("Cannot create posts/comments: there are no users")

        posts = self._create_posts(
            fake, users, categories, tags, post_count,
            require_published=comment_count > 0,
        )
        published = [post for post in posts if post.status == Post.Status.PUBLISHED]
        if comment_count and not published:
            raise CommandError("Cannot create comments: there are no published posts")
        self._create_comments(fake, users, published, comment_count)

        self.stdout.write(f"Users: {user_count} created")
        self.stdout.write(f"Categories: {self._category_created} created")
        self.stdout.write(f"Tags: {self._tag_created} created")
        self.stdout.write(f"Posts: {post_count} created")
        self.stdout.write(f"Comments: {comment_count} created")
        self.stdout.write(self.style.SUCCESS(f"Done in {perf_counter() - started:.2f} seconds"))

    def _clear(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Existing demo data cleared (superusers preserved).")

    def _create_users(self, fake: Faker, count: int) -> list[User]:
        used_emails = set(User.objects.values_list("email", flat=True))
        hashed_password = make_password(SEED_PASSWORD)
        pending: list[User] = []
        for _ in range(count):
            first_name = fake.first_name()[:50]
            last_name = fake.last_name()[:50]
            stem = slugify(f"{first_name}.{last_name}").replace("-", ".") or "user"
            email = f"{stem}@example.com".lower()
            suffix = FIRST_DUPLICATE_SUFFIX
            while email in used_emails:
                email = f"{stem}.{suffix}@example.com".lower()
                suffix += 1
            used_emails.add(email)
            pending.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=hashed_password,
                    is_active=random.random() >= INACTIVE_RATIO,
                    is_staff=random.random() < STAFF_RATIO,
                )
            )
        User.objects.bulk_create(pending)
        return list(User.objects.all())

    def _create_named(self, model: type, names: tuple[str, ...]) -> list:
        existing = set(model.objects.values_list("slug", flat=True))
        pending = []
        for name in names:
            slug = slugify(name)
            if slug not in existing:
                pending.append(model(name=name, slug=slug))
                existing.add(slug)
        model.objects.bulk_create(pending)
        if model is Category:
            self._category_created = len(pending)
        else:
            self._tag_created = len(pending)
        return list(model.objects.all())

    def _create_posts(
        self, fake: Faker, users: list[User], categories: list[Category],
        tags: list[Tag], count: int, require_published: bool,
    ) -> list[Post]:
        existing_slugs = set(Post.objects.values_list("slug", flat=True))
        published_exists = Post.objects.filter(status=Post.Status.PUBLISHED).exists()
        pending: list[Post] = []
        for index in range(count):
            title = fake.sentence(nb_words=POST_TITLE_WORDS).rstrip(".")[:200]
            base = (slugify(title) or "post")[:200]
            slug = base
            counter = FIRST_DUPLICATE_SUFFIX
            while slug in existing_slugs:
                suffix = f"-{counter}"
                slug = f"{base[:220 - len(suffix)]}{suffix}"
                counter += 1
            existing_slugs.add(slug)
            is_published = random.random() < PUBLISHED_RATIO
            if require_published and not published_exists and index == 0:
                is_published = True
            if is_published:
                published_exists = True
            pending.append(
                Post(
                    author=random.choice(users), title=title, slug=slug,
                    body="\n\n".join(
                        fake.paragraphs(nb=random.randint(MIN_PARAGRAPHS, MAX_PARAGRAPHS))
                    ),
                    status=Post.Status.PUBLISHED if is_published else Post.Status.DRAFT,
                    category=(
                        None if not categories or random.random() < UNCATEGORIZED_RATIO
                        else random.choice(categories)
                    ),
                )
            )
        Post.objects.bulk_create(pending)
        for post in pending:
            selected = random.sample(tags, k=random.randint(0, min(MAX_TAGS_PER_POST, len(tags))))
            post.tags.set(selected)
        return list(Post.objects.all())

    def _create_comments(
        self, fake: Faker, users: list[User], posts: list[Post], count: int,
    ) -> None:
        pending = [
            Comment(
                author=random.choice(users),
                post=random.choice(posts),
                body=" ".join(
                    fake.sentences(
                        nb=random.randint(MIN_COMMENT_SENTENCES, MAX_COMMENT_SENTENCES)
                    )
                ),
            )
            for _ in range(count)
        ]
        Comment.objects.bulk_create(pending)

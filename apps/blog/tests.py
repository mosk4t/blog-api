"""Tests for published and draft post visibility."""

from django.test import TestCase

from apps.auths.models import User
from apps.blog.models import Post


class PostVisibilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "author@example.com", password="strong-test-password-123",
            first_name="Author", last_name="One",
        )
        Post.objects.create(
            author=self.user, title="Published post", slug="published-post",
            body="Public content", status=Post.Status.PUBLISHED,
        )
        Post.objects.create(
            author=self.user, title="Draft post", slug="draft-post",
            body="Private content", status=Post.Status.DRAFT,
        )

    def test_anonymous_only_sees_published_posts(self):
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

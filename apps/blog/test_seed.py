"""Command integration tests for Homework 2."""

from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post, Tag


class SeedCommandTests(TestCase):
    def test_seeds_every_model(self):
        call_command("seed", users=3, posts=5, comments=11, stdout=StringIO())
        self.assertEqual(User.objects.filter(is_superuser=False).count(), 3)
        self.assertEqual(Category.objects.count(), 8)
        self.assertEqual(Tag.objects.count(), 20)
        self.assertEqual(Post.objects.count(), 5)
        self.assertEqual(Comment.objects.count(), 11)
        self.assertFalse(Comment.objects.exclude(post__status="published").exists())
        self.assertTrue(all(user.check_password("DemoPassword2026!") for user in User.objects.all()))

    def test_seeding_twice_does_not_crash(self):
        for _ in range(2):
            call_command("seed", users=1, posts=2, comments=2, stdout=StringIO())
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Post.objects.count(), 4)

    def test_clear_preserves_superusers(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="strong-test-password-123",
            first_name="Site", last_name="Admin",
        )
        call_command("seed", users=2, posts=2, comments=4, stdout=StringIO())
        call_command("seed", users=1, posts=1, comments=1, clear=True, stdout=StringIO())
        self.assertTrue(User.objects.filter(pk=superuser.pk).exists())
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Post.objects.count(), 1)

    def test_negative_numbers_are_rejected(self):
        with self.assertRaises(CommandError):
            call_command("seed", users=-1, posts=0, comments=0, stdout=StringIO())

    def test_missing_users_are_rejected(self):
        with self.assertRaises(CommandError):
            call_command("seed", users=0, posts=1, comments=0, stdout=StringIO())

    def test_missing_published_posts_are_rejected(self):
        with self.assertRaises(CommandError):
            call_command("seed", users=1, posts=0, comments=2, stdout=StringIO())

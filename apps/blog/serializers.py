"""Blog API representations."""

from rest_framework import serializers

from apps.blog.models import Category, Comment, Post, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class PostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "author", "author_email", "title", "slug", "body",
            "category", "tags", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author", "author_email", "created_at", "updated_at"]
        extra_kwargs = {"slug": {"required": False, "allow_blank": True}}

    def validate(self, attrs: dict) -> dict:
        if "slug" not in attrs or not attrs["slug"]:
            from django.utils.text import slugify

            from apps.blog.utils import unique_post_slug

            title = attrs.get("title", getattr(self.instance, "title", ""))
            if self.instance and not attrs.get("title"):
                return attrs
            attrs["slug"] = unique_post_slug(slugify(title), self.instance)
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "author_email", "body", "created_at"]
        read_only_fields = ["id", "author", "author_email", "created_at"]

    def validate_post(self, post: Post) -> Post:
        if post.status != Post.Status.PUBLISHED:
            raise serializers.ValidationError("Comments require a published post")
        return post

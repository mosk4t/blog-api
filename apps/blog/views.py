"""Blog REST API with queryset optimization and author-only modifications."""

from django.db.models import Q
from rest_framework import permissions, viewsets

from apps.blog.models import Category, Comment, Post, Tag
from apps.blog.permissions import IsAuthorOrReadOnly
from apps.blog.serializers import (
    CategorySerializer,
    CommentSerializer,
    PostSerializer,
    TagSerializer,
)


class StaffWritePermission(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.method in permissions.SAFE_METHODS or (
            bool(request.user and request.user.is_staff)
        )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [StaffWritePermission]
    lookup_field = "slug"


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [StaffWritePermission]
    lookup_field = "slug"


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Post.objects.select_related("author", "category").prefetch_related(
            "tags"
        )
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return queryset
        if user.is_authenticated:
            return queryset.filter(
                Q(status=Post.Status.PUBLISHED) | Q(author=user)
            )
        return queryset.filter(status=Post.Status.PUBLISHED)

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.select_related("author", "post")
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(post__status=Post.Status.PUBLISHED)

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user)

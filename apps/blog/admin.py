"""Feature-rich Django Unfold administration for blog content."""

from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import Truncator
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
from unfold.sections import TableSection

from apps.blog.models import Category, Comment, Post, Tag

COMMENT_PREVIEW_CHARS = 70
COMMENTS_PER_PAGE = 10


class CategoryPostsSection(TableSection):
    verbose_name = "Posts in this category"
    related_name = "posts"
    fields = ["title", "status", "created_at"]


class PostCommentsSection(TableSection):
    verbose_name = "Comments on this post"
    related_name = "comments"
    fields = ["body", "author", "created_at"]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "post_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_sections = [CategoryPostsSection]

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .annotate(_post_count=Count("posts", distinct=True))
            .prefetch_related("posts")
        )

    @display(description="Posts", ordering="_post_count")
    def post_count(self, obj: Category) -> int:
        return obj._post_count


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug", "post_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_post_count=Count("posts", distinct=True))

    @display(description="Posts", ordering="_post_count")
    def post_count(self, obj: Tag) -> int:
        return obj._post_count


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("post_title", "author", "body_preview", "created_at")
    list_filter = (
        ("post", AutocompleteSelectFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    )
    list_filter_submit = True
    autocomplete_fields = ("post", "author")
    search_fields = ("body", "author__email", "post__title")
    list_select_related = ("author", "post")
    list_per_page = 30

    @display(description="Post", ordering="post__title")
    def post_title(self, obj: Comment) -> str:
        return obj.post.title

    @display(description="Comment")
    def body_preview(self, obj: Comment) -> str:
        return Truncator(obj.body).chars(COMMENT_PREVIEW_CHARS)


class CommentInline(TabularInline):
    model = Comment
    tab = True
    per_page = COMMENTS_PER_PAGE
    extra = 0
    autocomplete_fields = ("author",)
    fields = ("author", "body", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        "post_header", "status_badge", "category", "tag_dropdown",
        "comments_count", "created_at",
    )
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("tags", MultipleRelatedDropdownFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    )
    list_filter_submit = True
    list_sections = [PostCommentsSection]
    list_per_page = 30
    search_fields = ("title", "body", "author__email")
    autocomplete_fields = ("author", "category", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    warn_unsaved_form = True
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}
    inlines = [CommentInline]
    fieldsets = (
        ("Content", {"classes": ["tab"], "fields": ("title", "slug", "body")}),
        ("Classification", {"classes": ["tab"], "fields": ("category", "tags", "status")}),
        ("Meta", {"classes": ["tab"], "fields": ("author", "created_at", "updated_at")}),
    )
    actions = ["publish_selected", "move_to_drafts"]
    actions_row = ["toggle_status"]
    actions_list = ["publish_all_drafts"]
    actions_detail = ["open_comments"]
    actions_submit_line = ["save_and_publish"]

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related("author", "category")
            .prefetch_related("tags", "comments__author")
            .annotate(_comments_count=Count("comments", distinct=True))
        )

    @display(description="Post", header=True, ordering="title")
    def post_header(self, obj: Post) -> tuple[str, str, str]:
        initials = f"{obj.author.first_name[:1]}{obj.author.last_name[:1]}".upper()
        return obj.title, obj.author.email, initials

    @display(description="Status", ordering="status", label={"published": "success", "draft": "warning"})
    def status_badge(self, obj: Post) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description="Tags", dropdown=True)
    def tag_dropdown(self, obj: Post) -> dict:
        tag_list = list(obj.tags.all())  # Prefetched: no extra database query.
        return {
            "title": f"{len(tag_list)} tags",
            "items": [{"title": tag.name} for tag in tag_list] or [{"title": "No tags"}],
        }

    @display(description="Comments", ordering="_comments_count")
    def comments_count(self, obj: Post) -> int:
        return obj._comments_count

    @action(description="Publish selected")
    def publish_selected(self, request, queryset) -> None:
        number = queryset.update(status=Post.Status.PUBLISHED)
        self.message_user(request, f"Published {number} posts")

    @action(description="Move to drafts")
    def move_to_drafts(self, request, queryset) -> None:
        number = queryset.update(status=Post.Status.DRAFT)
        self.message_user(request, f"Moved {number} posts to drafts")

    @action(description="Publish / unpublish", icon="published_with_changes", permissions=["blog.change_post"])
    def toggle_status(self, request: HttpRequest, object_id: int):
        post = self.get_object(request, object_id)
        if post is not None:
            post.status = (
                Post.Status.DRAFT if post.status == Post.Status.PUBLISHED
                else Post.Status.PUBLISHED
            )
            post.save(update_fields=["status", "updated_at"])
            self.message_user(request, f"{post.title}: {post.get_status_display()}")
        return redirect("admin:blog_post_changelist")

    @action(description="Publish all drafts", icon="publish", permissions=["blog.change_post"])
    def publish_all_drafts(self, request: HttpRequest):
        number = Post.objects.filter(status=Post.Status.DRAFT).update(
            status=Post.Status.PUBLISHED
        )
        self.message_user(request, f"Published {number} drafts")
        return redirect("admin:blog_post_changelist")

    @action(description="Open this post's comments", icon="chat")
    def open_comments(self, request: HttpRequest, object_id: int):
        url = reverse("admin:blog_comment_changelist")
        return redirect(f"{url}?post__id__exact={object_id}")

    @action(description="Save & publish", icon="publish", permissions=["blog.change_post"])
    def save_and_publish(self, request: HttpRequest, obj: Post) -> None:
        obj.status = Post.Status.PUBLISHED
        obj.save(update_fields=["status", "updated_at"])
        self.message_user(request, "Saved and published")

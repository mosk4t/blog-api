"""Blog-specific Unfold theme settings, imported by settings/base.py."""

from django.templatetags.static import static
from django.urls import reverse, reverse_lazy

from settings.conf import config

GITHUB_URL = config(
    "BLOG_GITHUB_URL", default="https://github.com/your-username/blog-api"
)

UNFOLD = {
    "SITE_TITLE": "Blog API Admin",
    "SITE_HEADER": "Blog Studio",
    "SITE_SUBHEADER": "Editorial workspace",
    "SITE_SYMBOL": "article",
    "BORDER_RADIUS": "8px",
    "ENVIRONMENT": "apps.blog.callbacks.environment_badge",
    "DASHBOARD_CALLBACK": "apps.blog.callbacks.dashboard_callback",
    "COMMAND": {"search_models": True, "show_history": True},
    "STYLES": [lambda request: static("css/blog-admin.css")],
    "COLORS": {
        "primary": {
            "50": "#f0fdfa", "100": "#ccfbf1", "200": "#99f6e4",
            "300": "#5eead4", "400": "#2dd4bf", "500": "#14b8a6",
            "600": "#0d9488", "700": "#0f766e", "800": "#115e59",
            "900": "#134e4a", "950": "#042f2e",
        },
    },
    "SITE_DROPDOWN": [
        {"icon": "code", "title": "GitHub repository", "link": GITHUB_URL},
        {"icon": "school", "title": "Unfold documentation", "link": "https://unfoldadmin.com/docs/"},
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Overview",
                "separator": False,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    }
                ],
            },
            {
                "title": "Content",
                "separator": True,
                "items": [
                    {
                        "title": "Posts",
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_post_changelist"),
                        "badge": "apps.blog.callbacks.draft_badge",
                        "badge_variant": "warning",
                    },
                    {
                        "title": "Comments",
                        "icon": "chat",
                        "link": reverse_lazy("admin:blog_comment_changelist"),
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                    },
                    {
                        "title": "Tags",
                        "icon": "sell",
                        "link": reverse_lazy("admin:blog_tag_changelist"),
                    },
                ],
            },
            {
                "title": "Users & Access",
                "separator": True,
                "permission": "apps.blog.callbacks.superuser_only",
                "items": [
                    {
                        "title": "Users",
                        "icon": "group",
                        "link": reverse_lazy("admin:auths_user_changelist"),
                        "permission": "apps.blog.callbacks.superuser_only",
                    },
                    {
                        "title": "Groups",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": "apps.blog.callbacks.superuser_only",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": ["blog.post"],
            "items": [
                {
                    "title": "All",
                    "link": reverse_lazy("admin:blog_post_changelist"),
                    "active": lambda request: not request.GET.get("status__exact"),
                },
                {
                    "title": "Published",
                    "link": lambda request: (
                        f"{reverse('admin:blog_post_changelist')}?status__exact=published"
                    ),
                    "active": lambda request: request.GET.get("status__exact") == "published",
                },
                {
                    "title": "Drafts",
                    "link": lambda request: (
                        f"{reverse('admin:blog_post_changelist')}?status__exact=draft"
                    ),
                    "active": lambda request: request.GET.get("status__exact") == "draft",
                },
            ],
        },
    ],
}


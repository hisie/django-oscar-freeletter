"""Test-only fork of Oscar's DashboardConfig that mounts both
freeletter_dashboard and blog_dashboard — the same fork a host project
needs to make, mirroring django-oscar-blog's own tests/dashboard.py
(this package's README points there for the pattern; this file is a
worked example of composing *two* such sections in one fork)."""

from __future__ import annotations

from django.apps import apps
from django.urls import include, path
from oscar.apps.dashboard.apps import DashboardConfig as OscarDashboardConfig


class DashboardConfig(OscarDashboardConfig):
    def ready(self):
        super().ready()
        self.freeletter_app = apps.get_app_config("freeletter_dashboard")
        self.blog_app = apps.get_app_config("blog_dashboard")

    def get_urls(self):
        urls = super().get_urls()
        urls.append(path("freeletter/", include(self.freeletter_app.urls[0])))
        urls.append(path("blog/", include(self.blog_app.urls[0])))
        return urls

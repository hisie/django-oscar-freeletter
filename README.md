# django-oscar-freeletter

Wires [django-freeletter](https://github.com/hisie/django-freeletter) into
[django-oscar](https://github.com/django-oscar/django-oscar): registers a
"product" issue-block type (and a "blog post" one, if
[django-oscar-blog](https://github.com/hisie/django-oscar-blog) is also
installed), plus an Oscar dashboard section for managing issues and
subscribers.

## What this package does, and doesn't, do

- Registers freeletter's `"product"` block type — an issue can feature a
  catalogue product, resolved via Oscar's own `Product` model, with no
  new lookup endpoint (it reuses Oscar's existing dashboard product
  autocomplete, `dashboard:catalogue-product-lookup`).
- Registers a `"blog_post"` block type **only if `oscar_blog` is
  installed** (checked at runtime via `apps.is_installed`, not imported
  unconditionally) — an issue can feature a `django-oscar-blog` post.
- An Oscar dashboard section (`oscar_freeletter.dashboard`) under
  `/dashboard/freeletter/`: issue list/create/update/delete with an
  inline block editor (pick "html" free content, a product, or — if
  installed — a blog post, per block), a one-click "queue for sending"
  action, and a read-only subscriber list.
- It does **not** ship its own models — everything it manages
  (`Issue`, `IssueBlock`, `Subscriber`) belongs to `django-freeletter`;
  this package only adds Oscar-specific block types and a dashboard UI
  on top.

## Installation

```
uv add django-oscar-freeletter
# or, with blog-post blocks too (pulls in django-oscar-blog):
uv add "django-oscar-freeletter[blog]"
```

Plain `pip` works the same way: `pip install django-oscar-freeletter[blog]`.
Without the `blog` extra, this package still installs and works fine — it
just registers the `"product"` block type only.

```python
INSTALLED_APPS = [
    ...,
    "freeletter",
    "oscar_blog.apps.OscarBlogConfig",              # optional — enables "blog_post" blocks
    "oscar_blog.dashboard.apps.BlogDashboardConfig", # optional
    "oscar_freeletter.apps.OscarFreeletterConfig",
    "oscar_freeletter.dashboard.apps.FreeletterDashboardConfig",
]
```

Run `manage.py migrate` (this package ships no migrations of its own —
`freeletter`'s migration is what actually creates the tables).

## Wiring the dashboard in

Same fork `django-oscar-blog` needs (Oscar's `DashboardConfig.get_urls()`
is a hardcoded list, not auto-discovered) — see this package's own
`tests/dashboard.py` for a worked example that mounts *both*
`freeletter_dashboard` and `blog_dashboard` in the same fork:

```python
from django.apps import apps
from django.urls import include, path
from oscar.apps.dashboard.apps import DashboardConfig as OscarDashboardConfig


class DashboardConfig(OscarDashboardConfig):
    def ready(self):
        super().ready()
        self.freeletter_app = apps.get_app_config("freeletter_dashboard")

    def get_urls(self):
        urls = super().get_urls()
        urls.append(path("freeletter/", include(self.freeletter_app.urls[0])))
        return urls
```

Then add a nav entry (e.g. under **Content**, alongside blog posts) via
`OSCAR_DASHBOARD_NAVIGATION`:

```python
{
    "label": _("Newsletter issues"),
    "url_name": "dashboard:freeletter-issue-list",
},
```

## Development

```
uv sync
uv run pytest
```

Requires `django-freeletter` and (for the "blog_post" tests)
`django-oscar-blog` — both wired in `pyproject.toml`'s `[tool.uv.sources]`
as local path dependencies until they're published.

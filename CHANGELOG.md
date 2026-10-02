# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.1] - 2026-10-02

### Changed

- Widened the `django-freeletter` dependency constraint from
  `>=0.1.0,<0.2` to `>=0.1.0,<1.0` — matches this project family's wider
  version-pinning policy going forward.
- The `blog` extra's `django-oscar-blog` constraint (and the matching
  dev-group entry, used to test the `blog_post` block type) is now
  `>=0.4.0,<1.0`, not just a widened upper bound: the old `>=0.1.0` floor
  let the lockfile drift all the way down to `0.2.0` — confirmed live,
  this actually broke the test suite (`NodeNotFoundError` on
  `oscar_blog`'s tags migration, since `taggit` only became a real
  `oscar_blog` dependency at its own `0.3.0`). `0.4.0` is the version this
  package is actually built and tested against.
- Removed the now-stale `[tool.uv.sources]` local-path overrides for
  `django-freeletter` and `django-oscar-blog` — both genuinely published
  now, no longer need path dependencies for local development.

## [0.1.0] - 2026-09-29

### Added

- Registers freeletter's `"product"` block type (always — reuses Oscar's
  existing `dashboard:catalogue-product-lookup`, no new endpoint) and a
  `"blog_post"` block type, registered only when `oscar_blog` is
  installed (`apps.is_installed("oscar_blog")`, not an unconditional
  import) — available via the `blog` extra
  (`django-oscar-freeletter[blog]`).
- An Oscar dashboard section under `/dashboard/freeletter/`: issue list/
  create/update/delete with an inline block-picker formset (html/
  product/blog post per row), a one-click "queue for sending" action,
  and a read-only subscriber list.
- 14 tests, 95% coverage.

[Unreleased]: https://github.com/hisie/django-oscar-freeletter/compare/0.1.1...HEAD
[0.1.1]: https://github.com/hisie/django-oscar-freeletter/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/hisie/django-oscar-freeletter/releases/tag/0.1.0

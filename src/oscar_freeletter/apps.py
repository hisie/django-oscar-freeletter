from oscar.core.application import OscarConfig


class OscarFreeletterConfig(OscarConfig):
    name = "oscar_freeletter"
    label = "oscar_freeletter"
    verbose_name = "Freeletter (Oscar integration)"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from django.apps import apps
        from freeletter.blocks import BlockType, register_block_type

        # Always available: this package already hard-depends on
        # django-oscar, so catalogue.Product always exists.
        register_block_type(
            BlockType(
                slug="product",
                label="Product",
                template_name="oscar_freeletter/blocks/product.html",
            )
        )

        # Only if django-oscar-blog is actually installed — an optional
        # dependency (see pyproject.toml's "blog" extra), checked at
        # runtime rather than imported unconditionally, so a project using
        # oscar_freeletter without the blog app doesn't break.
        if apps.is_installed("oscar_blog"):
            register_block_type(
                BlockType(
                    slug="blog_post",
                    label="Blog post",
                    template_name="oscar_freeletter/blocks/blog_post.html",
                )
            )

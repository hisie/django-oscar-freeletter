from freeletter.blocks import get_block_type, is_registered


def test_product_block_type_is_always_registered():
    assert is_registered("product")
    block_type = get_block_type("product")
    assert block_type.requires_object is True


def test_blog_post_block_type_is_registered_when_oscar_blog_is_installed():
    # tests/settings.py always installs oscar_blog, so this exercises the
    # "installed" branch of apps.py's conditional registration. The
    # "not installed" branch (the field/choice not existing at all) isn't
    # covered here — it would need a second settings module without
    # oscar_blog, which isn't worth the duplication for one conditional.
    assert is_registered("blog_post")

import pytest
from freeletter.models import Issue, IssueBlock
from oscar.test.factories import create_product
from oscar_blog.models import Post

pytestmark = pytest.mark.django_db


def test_product_block_renders_title_and_link():
    product = create_product(title="Palmera")
    issue = Issue.objects.create(title="Issue", slug="issue")
    block = IssueBlock.objects.create(issue=issue, block_type="product", content_object=product)

    html = block.render()

    assert "Palmera" in html
    assert product.get_absolute_url() in html


def test_blog_post_block_renders_title_and_excerpt():
    post = Post.objects.create(
        title="How to water a palm", slug="how-to-water", body="...", excerpt="Not too much."
    )
    issue = Issue.objects.create(title="Issue", slug="issue-2")
    block = IssueBlock.objects.create(issue=issue, block_type="blog_post", content_object=post)

    html = block.render()

    assert "How to water a palm" in html
    assert "Not too much." in html
    assert post.get_absolute_url() in html

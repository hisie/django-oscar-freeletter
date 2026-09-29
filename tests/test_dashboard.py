import pytest
from django.urls import reverse
from freeletter.models import Issue, IssueBlock, Subscriber
from oscar.test.factories import create_product
from oscar_blog.models import Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff_client(client, django_user_model):
    staff = django_user_model.objects.create_superuser(
        username="staff", email="staff@example.com", password="pw"
    )
    client.force_login(staff)
    return client


def test_anonymous_is_redirected_to_login(client):
    response = client.get(reverse("dashboard:freeletter-issue-list"))
    assert response.status_code == 302


def test_staff_can_list_issues(staff_client):
    Issue.objects.create(title="Autumn sale", slug="autumn-sale")

    response = staff_client.get(reverse("dashboard:freeletter-issue-list"))

    assert response.status_code == 200
    assert response.context["issue_list"].count() == 1


def _formset_management_data(prefix="blocks", total=1, initial=0):
    return {
        f"{prefix}-TOTAL_FORMS": str(total),
        f"{prefix}-INITIAL_FORMS": str(initial),
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
    }


def test_staff_can_create_issue_with_an_html_block(staff_client):
    data = {
        "title": "Autumn sale",
        "slug": "autumn-sale",
        "subject": "",
        **_formset_management_data(),
        "blocks-0-sortorder": "0",
        "blocks-0-block_type": "html",
        "blocks-0-html": "<p>20% off everything</p>",
        "blocks-0-product": "",
        "blocks-0-blog_post": "",
    }

    response = staff_client.post(reverse("dashboard:freeletter-issue-create"), data)

    assert response.status_code == 302, (
        response.context["block_formset"].errors if response.status_code == 200 else None
    )
    issue = Issue.objects.get(slug="autumn-sale")
    assert issue.blocks.count() == 1
    assert issue.blocks.first().html == "<p>20% off everything</p>"


def test_staff_can_add_a_product_block(staff_client):
    product = create_product(title="Palmera")
    data = {
        "title": "Autumn sale",
        "slug": "autumn-sale-2",
        "subject": "",
        **_formset_management_data(),
        "blocks-0-sortorder": "0",
        "blocks-0-block_type": "product",
        "blocks-0-html": "",
        "blocks-0-product": str(product.pk),
        "blocks-0-blog_post": "",
    }

    response = staff_client.post(reverse("dashboard:freeletter-issue-create"), data)

    assert response.status_code == 302
    issue = Issue.objects.get(slug="autumn-sale-2")
    block = issue.blocks.get()
    assert block.block_type == "product"
    assert block.content_object == product


def test_product_block_without_a_selected_product_is_rejected(staff_client):
    data = {
        "title": "Autumn sale",
        "slug": "autumn-sale-3",
        "subject": "",
        **_formset_management_data(),
        "blocks-0-sortorder": "0",
        "blocks-0-block_type": "product",
        "blocks-0-html": "",
        "blocks-0-product": "",
        "blocks-0-blog_post": "",
    }

    response = staff_client.post(reverse("dashboard:freeletter-issue-create"), data)

    assert response.status_code == 200
    assert not Issue.objects.filter(slug="autumn-sale-3").exists()
    assert "product" in response.context["block_formset"].forms[0].errors


def test_staff_can_add_a_blog_post_block(staff_client):
    post = Post.objects.create(title="Watering tips", slug="watering-tips", body="...")
    data = {
        "title": "Autumn sale",
        "slug": "autumn-sale-4",
        "subject": "",
        **_formset_management_data(),
        "blocks-0-sortorder": "0",
        "blocks-0-block_type": "blog_post",
        "blocks-0-html": "",
        "blocks-0-product": "",
        "blocks-0-blog_post": str(post.pk),
    }

    response = staff_client.post(reverse("dashboard:freeletter-issue-create"), data)

    assert response.status_code == 302
    issue = Issue.objects.get(slug="autumn-sale-4")
    block = issue.blocks.get()
    assert block.block_type == "blog_post"
    assert block.content_object == post


def test_updating_an_existing_block_preloads_its_selected_product(staff_client):
    product = create_product(title="Palmera")
    issue = Issue.objects.create(title="Issue", slug="issue")
    IssueBlock.objects.create(issue=issue, block_type="product", content_object=product)

    response = staff_client.get(
        reverse("dashboard:freeletter-issue-update", kwargs={"pk": issue.pk})
    )

    formset = response.context["block_formset"]
    assert formset.forms[0].fields["product"].initial == product


def test_queue_action_only_affects_draft_issues(staff_client):
    issue = Issue.objects.create(title="Issue", slug="issue", status=Issue.Status.DRAFT)

    response = staff_client.post(
        reverse("dashboard:freeletter-issue-queue", kwargs={"pk": issue.pk})
    )

    assert response.status_code == 302
    issue.refresh_from_db()
    assert issue.status == Issue.Status.QUEUED
    assert issue.queued_at is not None


def test_staff_can_delete_issue(staff_client):
    issue = Issue.objects.create(title="Issue", slug="issue")

    response = staff_client.post(
        reverse("dashboard:freeletter-issue-delete", kwargs={"pk": issue.pk})
    )

    assert response.status_code == 302
    assert not Issue.objects.filter(pk=issue.pk).exists()


def test_subscriber_list_view(staff_client):
    Subscriber.objects.create(email="a@example.com", is_confirmed=True)

    response = staff_client.get(reverse("dashboard:freeletter-subscriber-list"))

    assert response.status_code == 200
    assert response.context["subscribers"].count() == 1

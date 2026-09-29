from django import forms
from django.apps import apps
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from freeletter.models import Issue, IssueBlock
from oscar.apps.dashboard.catalogue.widgets import ProductSelect
from oscar.core.loading import get_model

Product = get_model("catalogue", "Product")

# Checked once at import time (after app loading, since forms.py is only
# ever imported lazily via get_class — see dashboard/views.py), not
# per-request: whether the "blog_post" block type's own field even exists
# on this form is fixed for the process's lifetime, same as which apps are
# installed.
BLOG_POST_INSTALLED = apps.is_installed("oscar_blog")

if BLOG_POST_INSTALLED:
    Post = get_model("oscar_blog", "Post")


class IssueSearchForm(forms.Form):
    title = forms.CharField(required=False, label=_("Title"))
    status = forms.ChoiceField(
        required=False,
        label=_("Status"),
        choices=[("", "---------"), *Issue.Status.choices],
    )


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ("title", "slug", "subject")


def _block_type_choices():
    from freeletter.blocks import get_registered_block_types

    return [(block_type.slug, block_type.label) for block_type in get_registered_block_types()]


class IssueBlockForm(forms.ModelForm):
    """One row of the issue-block formset. block_type picks which of the
    payload fields actually gets used — "product"/"blog_post" is a small,
    fixed set of *known* non-html block types this package itself
    registers (oscar_freeletter/apps.py); a third-party block type
    registered elsewhere wouldn't get a picker field here, only "html"'s
    plain fields and whatever raw admin editing freeletter's own admin.py
    already provides.
    """

    block_type = forms.ChoiceField(label=_("Block type"), choices=_block_type_choices)
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label=_("Product"),
        widget=ProductSelect(attrs={"class": "select2 product-select"}),
    )
    if BLOG_POST_INSTALLED:
        blog_post = forms.ModelChoiceField(
            queryset=Post.objects.all(), required=False, label=_("Blog post")
        )

    class Meta:
        model = IssueBlock
        fields = ("sortorder", "block_type", "html", "image")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance is not None and instance.pk:
            if instance.block_type == "product":
                self.fields["product"].initial = instance.content_object
            elif BLOG_POST_INSTALLED and instance.block_type == "blog_post":
                self.fields["blog_post"].initial = instance.content_object

    def clean(self):
        cleaned_data = super().clean()
        if not self.has_changed():
            # An untouched "extra" row at the end of the formset — nothing
            # to validate, Django's own formset machinery discards it.
            return cleaned_data

        block_type = cleaned_data.get("block_type")
        if block_type == "product" and not cleaned_data.get("product"):
            self.add_error("product", _("Select a product for this block."))
        if BLOG_POST_INSTALLED and block_type == "blog_post" and not cleaned_data.get("blog_post"):
            self.add_error("blog_post", _("Select a blog post for this block."))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.block_type == "product":
            instance.content_object = self.cleaned_data.get("product")
        elif BLOG_POST_INSTALLED and instance.block_type == "blog_post":
            instance.content_object = self.cleaned_data.get("blog_post")
        else:
            instance.content_object = None
        if commit:
            instance.save()
        return instance


IssueBlockFormSet = inlineformset_factory(
    Issue, IssueBlock, form=IssueBlockForm, extra=1, can_delete=True
)

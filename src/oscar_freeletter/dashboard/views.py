from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from freeletter.models import Issue, Subscriber
from oscar.core.loading import get_classes

IssueSearchForm, IssueForm, IssueBlockFormSet = get_classes(
    "oscar_freeletter.dashboard.forms", ("IssueSearchForm", "IssueForm", "IssueBlockFormSet")
)


class IssueListView(generic.ListView):
    template_name = "oscar/dashboard/freeletter/index.html"
    model = Issue
    form_class = IssueSearchForm
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    desc_template = "%(main_filter)s%(title_filter)s%(status_filter)s"

    def get_queryset(self):
        # pylint: disable=attribute-defined-outside-init
        self.desc_ctx = {"main_filter": _("All issues"), "title_filter": "", "status_filter": ""}
        queryset = self.model.objects.all()

        # pylint: disable=attribute-defined-outside-init
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data
        if data["title"]:
            queryset = queryset.filter(title__icontains=data["title"])
            self.desc_ctx["title_filter"] = _(" with title containing '%s'") % data["title"]
        if data["status"]:
            queryset = queryset.filter(status=data["status"])
            self.desc_ctx["status_filter"] = _(" with status '%s'") % data["status"]

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        context["queryset_description"] = self.desc_template % self.desc_ctx
        return context


class IssueBlockFormSetMixin:
    """Shared create/update handling for an Issue plus its ordered
    IssueBlockFormSet — same "one page, one save" shape as Oscar's own
    dashboard product-plus-stockrecord forms, just via a plain Django
    inline formset rather than Oscar's own formset helpers (those are
    catalogue-specific)."""

    template_name = "oscar/dashboard/freeletter/update.html"
    model = Issue
    form_class = IssueForm
    context_object_name = "issue"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["block_formset"] = IssueBlockFormSet(self.request.POST, instance=self.object)
        else:
            context["block_formset"] = IssueBlockFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        block_formset = context["block_formset"]
        if not block_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()
        block_formset.instance = self.object
        block_formset.save()

        messages.success(self.request, _("Issue '%s' saved") % self.object.title)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("dashboard:freeletter-issue-list")


class IssueCreateView(IssueBlockFormSetMixin, generic.CreateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = _("Create new issue")
        return ctx


class IssueUpdateView(IssueBlockFormSetMixin, generic.UpdateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.object.title
        return ctx


class IssueDeleteView(generic.DeleteView):
    template_name = "oscar/dashboard/freeletter/delete.html"
    model = Issue

    def get_success_url(self):
        messages.success(self.request, _("Deleted issue '%s'") % self.object.title)
        return reverse("dashboard:freeletter-issue-list")


class IssueQueueView(generic.View):
    """A one-click action, not a form — mirrors freeletter's own admin
    action (freeletter/admin.py's queue_for_sending), just reachable from
    the dashboard list instead."""

    def post(self, request, *args, **kwargs):
        issue = get_object_or_404(Issue, pk=kwargs["pk"])
        if issue.status == Issue.Status.DRAFT:
            issue.queue()
            messages.success(request, _("Issue '%s' queued for sending") % issue.title)
        return HttpResponseRedirect(reverse("dashboard:freeletter-issue-list"))


class SubscriberListView(generic.ListView):
    template_name = "oscar/dashboard/freeletter/subscribers.html"
    model = Subscriber
    context_object_name = "subscribers"
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE

from django.urls import path
from django.utils.translation import gettext_lazy as _
from oscar.core.application import OscarDashboardConfig
from oscar.core.loading import get_class


class FreeletterDashboardConfig(OscarDashboardConfig):
    label = "freeletter_dashboard"
    name = "oscar_freeletter.dashboard"
    verbose_name = _("Freeletter dashboard")

    default_permissions = [
        "is_staff",
    ]

    def configure_permissions(self):
        DashboardPermission = get_class("dashboard.permissions", "DashboardPermission")

        self.permissions_map = {
            "freeletter-issue-list": DashboardPermission.get("freeletter", "view_issue"),
            "freeletter-issue-create": DashboardPermission.get(
                "freeletter", "view_issue", "add_issue"
            ),
            "freeletter-issue-update": DashboardPermission.get(
                "freeletter", "view_issue", "change_issue"
            ),
            "freeletter-issue-delete": DashboardPermission.get(
                "freeletter", "view_issue", "delete_issue"
            ),
            "freeletter-issue-queue": DashboardPermission.get(
                "freeletter", "view_issue", "change_issue"
            ),
            "freeletter-subscriber-list": DashboardPermission.get("freeletter", "view_subscriber"),
        }

    # pylint: disable=attribute-defined-outside-init
    def ready(self):
        self.list_view = get_class("oscar_freeletter.dashboard.views", "IssueListView")
        self.create_view = get_class("oscar_freeletter.dashboard.views", "IssueCreateView")
        self.update_view = get_class("oscar_freeletter.dashboard.views", "IssueUpdateView")
        self.delete_view = get_class("oscar_freeletter.dashboard.views", "IssueDeleteView")
        self.queue_view = get_class("oscar_freeletter.dashboard.views", "IssueQueueView")
        self.subscriber_list_view = get_class(
            "oscar_freeletter.dashboard.views", "SubscriberListView"
        )
        self.configure_permissions()

    def get_urls(self):
        urls = [
            path("", self.list_view.as_view(), name="freeletter-issue-list"),
            path("create/", self.create_view.as_view(), name="freeletter-issue-create"),
            path("update/<int:pk>/", self.update_view.as_view(), name="freeletter-issue-update"),
            path("delete/<int:pk>/", self.delete_view.as_view(), name="freeletter-issue-delete"),
            path("queue/<int:pk>/", self.queue_view.as_view(), name="freeletter-issue-queue"),
            path(
                "subscribers/",
                self.subscriber_list_view.as_view(),
                name="freeletter-subscriber-list",
            ),
        ]
        return self.post_process_urls(urls)

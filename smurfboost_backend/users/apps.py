import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "smurfboost_backend.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import smurfboost_backend.users.signals  # noqa: F401, PLC0415

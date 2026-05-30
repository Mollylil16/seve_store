from django.apps import AppConfig


class VendorConfig(AppConfig):
    name = "vendor"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import vendor.admin.admin  # noqa

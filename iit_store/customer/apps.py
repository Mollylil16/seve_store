from django.apps import AppConfig


class CustomerConfig(AppConfig):
    name = "customer"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import customer.admin.admin  # noqa

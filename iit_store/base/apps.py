from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = "base"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import base.models.profil  # noqa — charge le signal post_save
        import base.admin.admin    # noqa — enregistre l'admin

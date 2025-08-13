from django.apps import AppConfig


class ExampleConfig(AppConfig):
    name = "example"
    default_auto_field = "django.db.models.BigAutoField"

    # def ready(self):
    # from actstream import registry
    # registry.register(get_user_model())

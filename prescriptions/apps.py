from django.apps import AppConfig


class PrescriptionsConfig(AppConfig):
    """Configuration for the prescriptions app, managing medication catalog and prescriptions."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescriptions'

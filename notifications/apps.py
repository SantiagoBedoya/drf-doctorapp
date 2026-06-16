from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Django AppConfig for the notifications application.

    Handles signal registration for appointment-related notifications.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        import notifications.signals

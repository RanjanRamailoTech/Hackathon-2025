from django.apps import AppConfig


class JobOpeningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Job_opening'

    def ready(self):
        import Job_opening.signals
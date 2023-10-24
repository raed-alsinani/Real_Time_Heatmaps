from django.apps import AppConfig
from . import utils


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        self.configure_app()


    def configure_app(self):
        utils.my_callback(__name__)

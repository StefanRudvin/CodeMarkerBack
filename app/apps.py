from django.apps import AppConfig


class CodeMarkerConfig(AppConfig):
    name = 'app'

    def ready(self):
        from . import signals

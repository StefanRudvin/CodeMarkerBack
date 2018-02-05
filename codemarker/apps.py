from django.apps import AppConfig


class CodeMarkerConfig(AppConfig):
    name = 'codemarker'

    def ready(self):
        from . import signals

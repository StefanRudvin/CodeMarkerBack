"""
Auto-generated module by Django registering the app with the service

@TeamAlpha 2018
CodeMarker
apps.py
"""

from django.apps import AppConfig


class CodeMarkerConfig(AppConfig):
    name = 'app'

    def ready(self):
        from . import signals

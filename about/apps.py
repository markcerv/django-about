"""Django About app configuration."""

from django.apps import AppConfig


class AboutConfig(AppConfig):
    """Configuration for Django About app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'about'
    verbose_name = 'About'

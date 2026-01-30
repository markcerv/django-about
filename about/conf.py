"""Configuration for django-about."""

from django.conf import settings


DEFAULT_CONFIG = {
    "show_django_version": True,
    "show_python_version": True,
    "show_database_version": True,
    "show_celery_version": True,
    "show_redis_version": True,
    "show_git_info": True,
    "show_cache_stats": True,
    "show_third_party_apps": True,
    "show_dashboard_description": True,  # Show default dashboard description
    "page_title": "About",
    "page_intro": None,  # Optional intro text at top of page
    "release_env_vars": [
        "HEROKU_SLUG_COMMIT",
        "GIT_COMMIT",
        "COMMIT_SHA",
        "CI_COMMIT_SHA",
    ],
    "release_date_env_vars": [
        "HEROKU_RELEASE_CREATED_AT",
        "DEPLOY_DATE",
        "RELEASE_DATE",
    ],
    "important_integrations": {
        "sentry-sdk",
        "rollbar",
        "scout-apm",
        "redis",
        "django-redis",
        "whitenoise",
        "flower",
    },
    "custom_sections": [],  # For future extensibility
}


def get_config():
    """Get merged configuration (user settings + defaults)."""
    user_config = getattr(settings, "ABOUT_CONFIG", {})
    return {**DEFAULT_CONFIG, **user_config}

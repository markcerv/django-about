"""Version detection utilities for django-about."""

import django
import importlib
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from django.apps import apps
from importlib.metadata import (
    metadata,
    PackageNotFoundError,
    distributions,
    packages_distributions,
)


DIST_MAP = packages_distributions()


logger = logging.getLogger(__name__)


def get_django_version():
    """Get Django version."""
    try:
        return django.get_version()
    except Exception as e:
        logger.error(f"Error getting Django version: {e}")
        return "Error"


def get_python_version():
    """Get Python version."""
    try:
        return sys.version.split()[0]
    except Exception as e:
        logger.error(f"Error getting Python version: {e}")
        return "Error"


def get_database_version():
    """
    Get database version.
    Currently supports PostgreSQL, MySQL, and SQLite.
    """
    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_full = cursor.fetchone()[0]

            # PostgreSQL: "PostgreSQL 15.3 on x86_64..." -> "15.3"
            if "PostgreSQL" in db_full:
                return db_full.split()[1]
            # MySQL: "8.0.32-0ubuntu0.22.04.2" -> "8.0.32"
            elif "MySQL" in db_full or "MariaDB" in db_full:
                # Extract version from beginning of string
                match = re.search(r"(\d+\.\d+\.\d+)", db_full)
                if match:
                    return match.group(1)
            # SQLite
            elif "SQLite" in db_full:
                return db_full.split()[0]

            return db_full
    except Exception as e:
        logger.warning(f"Error getting database version: {e}")
        return None


def get_celery_version():
    """Get Celery version if installed."""
    try:
        import celery

        return celery.__version__
    except ImportError:
        return None
    except Exception as e:
        logger.warning(f"Error getting Celery version: {e}")
        return "Error"


def get_redis_version():
    """Get Redis server version if available."""
    try:
        from django.core.cache import cache

        redis_info = cache.client.get_client().info()
        return redis_info.get("redis_version")
    except Exception:
        # Fallback: try to get Redis client package version
        try:
            import redis

            return f"{redis.__version__} (client)"
        except ImportError:
            return None
        except Exception as e:
            logger.warning(f"Error getting Redis version: {e}")
            return None


def get_git_commit():
    """
    Get git commit hash.
    Checks environment variables first, then falls back to git command.
    """
    from .conf import get_config

    config = get_config()

    # Try environment variables first
    for env_var in config["release_env_vars"]:
        commit = os.environ.get(env_var)
        if commit:
            return commit

    # Fallback to git command
    try:
        import shutil

        # Check if git command exists
        if shutil.which("git") is None:
            return None

        commit = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )
            .decode("ascii")
            .strip()
        )

        return commit
    except Exception as e:
        logger.debug(f"Could not get git commit: {e}")
        return None


def get_git_origin_url():
    """
    Get the Git remote 'origin' URL.
    Checks environment variables first, then falls back to git command.
    Safe to use inside Django, even in Docker or production.
    """
    # 1. Check environment variables first
    # Allows overriding in Docker/CI/CD
    env_vars = ["GIT_ORIGIN_URL", "SOURCE_REPO", "REPO_URL"]
    for env_var in env_vars:
        url = os.environ.get(env_var)
        if url:
            return url

    # 2. Fallback to git command
    try:
        import shutil

        # Ensure git exists
        if shutil.which("git") is None:
            return None

        # Determine project root (two levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        url = (
            subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"],
                stderr=subprocess.DEVNULL,
                cwd=project_root,
            )
            .decode("utf-8")
            .strip()
        )

        return url or None

    except Exception as e:
        logger.debug(f"Could not get git origin URL: {e}")
        return None


def get_deployment_date():
    """
    Get deployment date.
    Checks environment variables first, then falls back to git commit date.
    """
    from .conf import get_config

    config = get_config()

    # Try environment variables first
    for env_var in config["release_date_env_vars"]:
        date_str = os.environ.get(env_var)
        if date_str:
            try:
                # Parse ISO 8601 format (e.g., "2025-10-28T01:11:55Z")
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except Exception as e:
                logger.warning(f"Could not parse date from {env_var}: {e}")
                continue

    # Fallback to git commit date
    try:
        import shutil

        # Check if git command exists
        if shutil.which("git") is None:
            return None

        commit_date_str = (
            subprocess.check_output(
                ["git", "show", "-s", "--format=%ci", "HEAD"],
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )
            .decode("ascii")
            .strip()
        )

        # Parse the date string to a timezone-aware datetime object
        # Format: "2025-10-27 14:07:21 -0700"
        match = re.match(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ([+-]\d{4})",
            commit_date_str,
        )
        if match:
            dt_str, tz_str = match.groups()
            # Parse the datetime part
            dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            # Parse timezone offset (e.g., "-0700" means UTC-7)
            tz_hours = int(tz_str[1:3])
            tz_mins = int(tz_str[3:5])
            if tz_str[0] == "-":
                tz_hours = -tz_hours
                tz_mins = -tz_mins
            # Create timezone-aware datetime
            tz = timezone(timedelta(hours=tz_hours, minutes=tz_mins))
            return dt_naive.replace(tzinfo=tz)
    except Exception as e:
        logger.debug(f"Could not get git commit date: {e}")
        return None

    return None


def get_distribution_name(module_name):
    dists = DIST_MAP.get(module_name)
    if not dists:
        return None
    return dists[0]


def extract_homepage(meta):
    home = meta.get("Home-page")
    if home and home.startswith(("http://", "https://")):
        return home.strip()

    project_url = meta.get("Project-URL")
    if not project_url:
        return None

    parts = [p.strip() for p in project_url.split(",")]
    for part in parts:
        if part.startswith(("http://", "https://")):
            return part

    return None


def get_third_party_app_info_grouped():
    """
    Returns a dict grouped by distribution:
    {
        "django-allauth": {
            "version": "65.14.0",
            "homepage": "https://allauth.org",
            "apps": ["allauth", "account", "socialaccount", ...]
        },
        "django-anymail": {
            "version": "...",
            "homepage": "...",
            "apps": ["anymail"]
        },
        ...
    }
    """
    grouped = {}

    for app_config in apps.get_app_configs():
        full_name = app_config.name

        # Skip Django built-ins
        if full_name.startswith("django.contrib"):
            continue

        module_name = full_name.split(".")[0]

        dist_name = get_distribution_name(module_name)
        if not dist_name:
            continue  # local app or unknown

        # Load metadata once per distribution
        if dist_name not in grouped:
            try:
                meta = metadata(dist_name)
            except PackageNotFoundError:
                continue

            grouped[dist_name] = {
                "version": meta.get("Version"),
                "homepage": extract_homepage(meta),
                "apps": [],
            }

        # Add this Django app label to the distribution group
        grouped[dist_name]["apps"].append(app_config.label)

    return grouped


def get_non_django_integrations(django_distributions):
    """
    Returns a list of third-party packages that:
    - are installed in site-packages
    - are NOT part of the Django app system
    - are NOT local project modules
    """
    results = []

    site_packages_paths = [p for p in sys.path if "site-packages" in p]

    for dist in distributions():
        name = dist.metadata["Name"]

        # Skip Django apps already detected
        if name in django_distributions:
            continue

        # Skip Django itself
        if name.startswith("Django"):
            continue

        # Skip local project modules
        try:
            module = importlib.import_module(name.replace("-", "_"))
            module_file = getattr(module, "__file__", "")
            if module_file and not any(
                module_file.startswith(p) for p in site_packages_paths
            ):
                continue
        except Exception:
            # If it can't be imported, skip it
            continue

        # Add it
        results.append(
            {
                "package_name": name,
                "version": dist.version,
                "homepage": dist.metadata.get("Home-page"),
            }
        )

    return results


def get_all_versions():
    """
    Get all version information.
    Returns a dictionary with all detected versions.
    """
    from .conf import get_config

    config = get_config()

    versions = {}

    if config["show_django_version"]:
        versions["django"] = get_django_version()

    if config["show_python_version"]:
        versions["python"] = get_python_version()

    if config["show_database_version"]:
        versions["database"] = get_database_version()

    if config["show_celery_version"]:
        versions["celery"] = get_celery_version()

    if config["show_redis_version"]:
        versions["redis"] = get_redis_version()

    if config["show_git_info"]:
        versions["git_commit"] = get_git_commit()
        versions["deployment_date"] = get_deployment_date()
        versions["git_origin_url"] = get_git_origin_url()

    if config["show_third_party_apps"]:
        versions["third_party_apps"] = get_third_party_app_info_grouped()
        # use the above to figure out non_django_integrations
        django_dist_names = set(versions["third_party_apps"].keys())
        versions["integrations"] = get_non_django_integrations(django_dist_names)

    return versions

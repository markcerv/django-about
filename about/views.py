"""Views for django-about."""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .cache_utils import get_cache_stats
from .conf import get_config
from .version_utils import get_all_versions


@staff_member_required
def system_info_view(request):
    """Display system version information."""
    config = get_config()

    # Get all version information
    versions = get_all_versions()

    # Get cache statistics if enabled
    cache_stats = None
    if config['show_cache_stats']:
        cache_stats = get_cache_stats()

    # Separate important vs other integrations
    important_integrations = []
    other_integrations = []

    if versions.get('integrations'):
        important_packages = config.get('important_integrations', set())

        for integration in versions['integrations']:
            if integration['package_name'] in important_packages:
                important_integrations.append(integration)
            else:
                other_integrations.append(integration)

        # Sort both lists by package name
        important_integrations.sort(key=lambda x: x['package_name'].lower())
        other_integrations.sort(key=lambda x: x['package_name'].lower())

    # Prepare custom sections
    custom_sections = []
    for section_func in config.get('custom_sections', []):
        try:
            section = section_func()
            custom_sections.append(section)
        except Exception as e:
            # Log error but don't break the page
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing custom section function: {e}")

    context = {
        'versions': versions,
        'cache_stats': cache_stats,
        'custom_sections': custom_sections,
        'important_integrations': important_integrations,
        'other_integrations': other_integrations,
        'config': config,
        'title': config['page_title'],
    }

    return render(request, 'about/dashboard.html', context)

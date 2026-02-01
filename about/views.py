"""Views for django-about."""

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render

from .cache_utils import get_cache_stats
from .conf import get_config
from .version_utils import (
    get_all_versions,
    get_non_django_integrations,
    get_third_party_app_info_grouped,
)


def _get_section_order(config, versions, cache_stats, custom_sections):
    """
    Build ordered list of sections to display.
    Returns list of section IDs in the order they should appear.
    """
    # Default order of sections
    default_order = [
        'dashboard_description',
        'page_intro',
        'code_info',
        'software_versions',
        'cache_stats',
        'third_party_apps',
        'third_party_integrations',
    ]

    # Add custom section IDs (these were set using function names)
    for section in custom_sections:
        section_id = section.get('id')
        if section_id:
            default_order.append(section_id)

    # Get user-specified order
    user_order = config.get('section_order')

    if user_order:
        # Start with user-specified order
        ordered = list(user_order)
        # Add any sections not in user order (that are enabled) at the end
        for section_id in default_order:
            if section_id not in ordered and _should_show_section(section_id, config, versions, cache_stats, custom_sections):
                ordered.append(section_id)
        return ordered
    else:
        # Use default order, filtering out disabled sections
        return [s for s in default_order if _should_show_section(s, config, versions, cache_stats, custom_sections)]


def _should_show_section(section_id, config, versions, cache_stats, custom_sections):
    """Check if a section should be displayed based on config and data availability."""
    if section_id == 'dashboard_description':
        return config.get('show_dashboard_description', True)
    elif section_id == 'page_intro':
        return config.get('page_intro') is not None
    elif section_id == 'code_info':
        return config.get('show_git_info') and (versions.get('git_commit') or versions.get('deployment_date'))
    elif section_id == 'software_versions':
        return any([
            config.get('show_django_version'),
            config.get('show_python_version'),
            config.get('show_database_version'),
            config.get('show_celery_version'),
            config.get('show_redis_version'),
        ])
    elif section_id == 'cache_stats':
        return config.get('show_cache_stats') and cache_stats is not None
    elif section_id == 'third_party_apps':
        return config.get('show_third_party_apps') and versions.get('third_party_apps')
    elif section_id == 'third_party_integrations':
        return config.get('show_third_party_apps') and versions.get('integrations')
    else:
        # Custom section - check if it exists (by ID)
        return any(
            section.get('id') == section_id for section in custom_sections
        )


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
    # Only show important integrations on initial load for performance
    important_integrations = []
    other_integrations_count = 0

    if versions.get('integrations'):
        important_packages = config.get('important_integrations', set())

        for integration in versions['integrations']:
            if integration['package_name'] in important_packages:
                important_integrations.append(integration)
            else:
                other_integrations_count += 1

        # Sort important integrations by package name
        important_integrations.sort(key=lambda x: x['package_name'].lower())

    # Prepare custom sections with IDs
    custom_sections = []
    for section_func in config.get('custom_sections', []):
        try:
            section = section_func()
            # Ensure section has an ID - use function name if not specified
            if 'id' not in section:
                # Use function name as ID (e.g., 'environment_info')
                section['id'] = section_func.__name__
            custom_sections.append(section)
        except Exception as e:
            # Log error but don't break the page
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing custom section function: {e}")

    # Get ordered list of sections
    section_order = _get_section_order(config, versions, cache_stats, custom_sections)

    context = {
        'versions': versions,
        'cache_stats': cache_stats,
        'custom_sections': custom_sections,
        'important_integrations': important_integrations,
        'other_integrations_count': other_integrations_count,
        'config': config,
        'title': config['page_title'],
        'section_order': section_order,
    }

    return render(request, 'about/dashboard.html', context)


@staff_member_required
def scan_integrations_view(request):
    """AJAX endpoint for lazy-loading other integrations."""
    config = get_config()

    # Get third-party apps to exclude from integrations list
    third_party_apps = get_third_party_app_info_grouped()
    django_dist_names = set(third_party_apps.keys())

    # Scan for non-Django integrations
    all_integrations = get_non_django_integrations(django_dist_names)

    # Separate important vs other
    important_packages = config.get('important_integrations', set())
    other_integrations = [
        integration for integration in all_integrations
        if integration['package_name'] not in important_packages
    ]

    # Sort by package name
    other_integrations.sort(key=lambda x: x['package_name'].lower())

    return JsonResponse({
        'integrations': other_integrations,
        'count': len(other_integrations)
    })

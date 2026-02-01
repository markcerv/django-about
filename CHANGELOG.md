# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-02-01

### Added
- **Performance Optimization**: Lazy-loading for "Other Integrations" via AJAX
  - Initial page load now scans only important integrations
  - Other integrations load on-demand when user clicks "Scan" button
  - Reduces page load time from between 1 to 10s to under 100ms in projects with 100+ packages
- **Section Ordering**: New `section_order` configuration option
  - Customize the order in which sections appear on the dashboard
  - "Forgiving" behavior: unlisted sections still appear at the end
  - Supports both built-in and custom sections
- **Section ID Discovery**: New `show_section_ids` configuration option
  - Display section IDs as gray badges next to section titles
  - Helps users discover section IDs for configuring `section_order`
  - Disabled by default to keep production interface clean
- **Consistent Styling**: Unified CSS classes for all section types
  - All sections (intro, description, content) now have consistent padding and alignment
  - Custom sections automatically inherit proper styling

### Changed
- Template refactored to use loop-based section rendering for better maintainability
- Custom section IDs now use function names instead of derived titles for clarity
- Improved JavaScript CSRF token handling using cookie-based approach

### Fixed
- Fixed section alignment issues where intro sections appeared narrower than content sections
- Fixed template operator precedence issues that caused duplicate section rendering

## [0.1.2] - 2026-01-30

### Added
- Added `__version__` attribute to package for programmatic version access

### Fixed
- Updated README screenshot URLs to use GitHub raw URLs for proper display on PyPI
- Screenshots now display correctly on both GitHub and PyPI

## [0.1.1] - 2026-01-30

### Changed
- Updated README with screenshots section instructions
- PyPI badges will display correctly once package is published to production PyPI

### Documentation
- Enhanced screenshots section in README for better visualization

## [0.1.0] - 2026-01-30

### Added
- Initial release of django-about
- Display Django, Python, PostgreSQL, Celery, and Redis versions
- Show git commit hash, deployment date, and repository URL
- Display cache statistics (read-only)
- Third-party Django apps detection grouped by distribution package
- Third-party integrations detection with important/other separation
- Custom page intro text via `page_intro` config option
- Django admin integration
- Configurable via ABOUT_CONFIG setting
- Support for custom information sections
- Graceful handling of optional dependencies
- Support for Django 3.2 through 5.2
- Support for Python 3.8 through 3.12

### Features
- Clean admin-styled interface
- Staff-only access control
- Environment variable detection for deployment info
- Automatic git detection in development
- Git origin URL detection
- Third-party apps grouped by distribution with version and homepage links
- Important integrations highlighted at top, others in collapsible accordion
- Configurable `important_integrations` list for custom prioritization
- Extensible architecture for custom sections

[0.1.3]: https://github.com/markcerv/django-about/releases/tag/v0.1.3
[0.1.2]: https://github.com/markcerv/django-about/releases/tag/v0.1.2
[0.1.1]: https://github.com/markcerv/django-about/releases/tag/v0.1.1
[0.1.0]: https://github.com/markcerv/django-about/releases/tag/v0.1.0

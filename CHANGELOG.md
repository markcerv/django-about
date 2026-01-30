# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.2]: https://github.com/markcerv/django-about/releases/tag/v0.1.2
[0.1.1]: https://github.com/markcerv/django-about/releases/tag/v0.1.1
[0.1.0]: https://github.com/markcerv/django-about/releases/tag/v0.1.0

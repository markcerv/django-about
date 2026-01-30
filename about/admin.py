"""Admin integration for django-about."""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse


class SystemInfoAdmin(admin.ModelAdmin):
    """
    Pseudo-admin class for About.
    This creates an entry in the admin index without requiring a real model.
    """

    def has_module_permission(self, request):
        """Show this module in admin index for staff users."""
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        """Hide the 'Add' button."""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow viewing the about."""
        return False
        # return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        """Hide delete functionality."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirect to the about dashboard instead of showing a changelist."""
        return redirect(reverse("about:dashboard"))


# Create a fake proxy model to register with admin
# This is a workaround to make about appear in the admin index
from django.contrib.auth.models import Group


class SystemInformation(Group):
    """Proxy model for About admin entry."""

    class Meta:
        proxy = True
        verbose_name = "About / version info"
        verbose_name_plural = "About / version info"
        app_label = "about"


# Register the proxy model with our custom admin
admin.site.register(SystemInformation, SystemInfoAdmin)

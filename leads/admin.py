from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count

from .models import Application, JobListing, Lead, Post, SavedJob, Service


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "domain", "predicted_domain", "handled", "created_at")
    list_filter = ("domain", "predicted_domain", "handled")
    search_fields = ("name", "email", "message")
    readonly_fields = ("predicted_domain", "created_at")


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "is_remote", "employment_type", "is_active", "created_at")
    list_filter = ("employment_type", "is_remote", "is_active")
    search_fields = ("title", "summary")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "created_at", "updated_at")
    list_filter = ("status", "job")
    search_fields = ("candidate__username", "candidate__email", "job__title")
    list_editable = ("status",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "created_at")
    search_fields = ("candidate__username", "job__title")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "domain", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("domain", "is_active")
    search_fields = ("title", "tagline", "description")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}


# --- Candidate Management -------------------------------------------------
# Swap in a richer view of Django's built-in User admin so HR can see who's
# actually applied, without needing a separate "Candidate" model.

class CandidateAdmin(DefaultUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "application_count", "is_active")
    ordering = ("-date_joined",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_application_count=Count("applications"))

    def application_count(self, obj):
        return obj._application_count

    application_count.short_description = "Applications"
    application_count.admin_order_field = "_application_count"


admin.site.unregister(User)
admin.site.register(User, CandidateAdmin)
admin.site.site_header = "Administration"
admin.site.site_title = "Administration"
admin.site.index_title = "KYK Informatics"

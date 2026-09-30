from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from leads import views as leads_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("leads.urls")),

    # Candidate account portal
    path("accounts/signup/", leads_views.signup_view, name="signup"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="portal/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("accounts/profile/", leads_views.profile_view, name="profile"),

    # Forgot password (Django's built-in reset flow — emails print to the
    # console in dev via EMAIL_BACKEND; see settings.py)
    path(
        "accounts/password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="portal/password_reset.html",
            email_template_name="portal/password_reset_email.html",
            subject_template_name="portal/password_reset_subject.txt",
            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "accounts/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="portal/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="portal/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="portal/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # Job board + applications
    path("jobs/", leads_views.job_list_view, name="job_list"),
    path("jobs/<int:job_id>/", leads_views.job_detail_view, name="job_detail"),
    path("jobs/<int:job_id>/apply/", leads_views.apply_view, name="apply"),
    path("jobs/<int:job_id>/save/", leads_views.toggle_save_job, name="toggle_save_job"),
    path("saved-jobs/", leads_views.saved_jobs_view, name="saved_jobs"),

    # Candidate dashboard
    path("dashboard/", leads_views.dashboard_view, name="dashboard"),

    # Public content, managed from /admin/
    path("services/", leads_views.service_list_view, name="service_list"),
    path("insights/", leads_views.post_list_view, name="post_list"),
    path("insights/<slug:slug>/", leads_views.post_detail_view, name="post_detail"),

    # HR / staff analytics
    path("hr/analytics/", leads_views.hr_analytics_view, name="hr_analytics"),

    # Serves /mnt/user-data/outputs/kyk-technologies.html if copied into templates/index.html
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

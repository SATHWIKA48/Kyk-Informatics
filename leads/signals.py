from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Application


@receiver(pre_save, sender=Application)
def _stash_previous_status(sender, instance, **kwargs):
    """Remember the status this Application had before this save, so the
    post_save handler below can tell whether it actually changed."""
    if instance.pk:
        try:
            instance._previous_status = Application.objects.get(pk=instance.pk).status
        except Application.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Application)
def _notify_status_change(sender, instance, created, **kwargs):
    """Email the candidate when HR/admin changes their application's status
    (e.g. Submitted -> Interview). Uses whatever EMAIL_BACKEND is configured
    — the console backend in dev, real SMTP/SES/etc. in production."""
    if created:
        return

    previous = getattr(instance, "_previous_status", None)
    if not previous or previous == instance.status or not instance.candidate.email:
        return

    send_mail(
        subject=f"Update on your application — {instance.job.title}",
        message=(
            f"Hi {instance.candidate.first_name or instance.candidate.username},\n\n"
            f"Your application for \"{instance.job.title}\" is now: "
            f"{instance.get_status_display()}.\n\n"
            "You can see full details anytime on your dashboard: "
            "http://127.0.0.1:8000/dashboard/\n\n"
            "— KYK Informatics"
        ),
        from_email=None,
        recipient_list=[instance.candidate.email],
        fail_silently=True,
    )

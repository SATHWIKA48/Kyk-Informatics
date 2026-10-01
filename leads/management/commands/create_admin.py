import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Creates a superuser from environment variables if one with that username
    doesn't already exist. Safe to run on every deploy (won't error or
    duplicate on repeat runs) — this is what makes it usable in a Build
    Command on hosts like Render's free tier, which has no Shell access.

    Reads: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL,
    DJANGO_SUPERUSER_PASSWORD. If any are unset, it skips quietly instead
    of failing the build.
    """

    help = "Create a superuser from env vars if it doesn't already exist."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "create_admin: DJANGO_SUPERUSER_USERNAME/PASSWORD not set — skipping."
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"create_admin: user '{username}' already exists — skipping.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"create_admin: created superuser '{username}'."))
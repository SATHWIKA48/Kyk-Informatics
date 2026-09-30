import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("leads", "0003_seed_jobs"),
    ]

    operations = [
        migrations.CreateModel(
            name="SavedJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_by",
                        to="leads.joblisting",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("candidate", "job")},
            },
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                (
                    "domain",
                    models.CharField(
                        choices=[
                            ("recruitment", "Global Recruitment"),
                            ("software", "Software & Web Development"),
                            ("ai", "AI · AGI · ASI"),
                            ("other", "Something else"),
                        ],
                        default="other",
                        max_length=20,
                    ),
                ),
                ("icon", models.CharField(blank=True, help_text="An emoji, e.g. 🤖", max_length=8)),
                ("tagline", models.CharField(blank=True, max_length=200)),
                ("description", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["order", "title"]},
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("excerpt", models.CharField(blank=True, max_length=300)),
                ("body", models.TextField()),
                ("is_published", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]

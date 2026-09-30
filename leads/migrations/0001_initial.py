from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobListing",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("location", models.CharField(blank=True, max_length=150)),
                ("is_remote", models.BooleanField(default=False)),
                (
                    "employment_type",
                    models.CharField(
                        choices=[
                            ("contract", "Contract Staffing"),
                            ("permanent", "Permanent Hiring"),
                            ("executive", "Executive Recruitment"),
                        ],
                        default="permanent",
                        max_length=40,
                    ),
                ),
                ("summary", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
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
                ("message", models.TextField()),
                (
                    "predicted_domain",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("recruitment", "Global Recruitment"),
                            ("software", "Software & Web Development"),
                            ("ai", "AI · AGI · ASI"),
                            ("other", "Something else"),
                        ],
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("handled", models.BooleanField(default=False)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]

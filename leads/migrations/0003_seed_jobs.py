from django.db import migrations


def seed_jobs(apps, schema_editor):
    JobListing = apps.get_model("leads", "JobListing")
    if JobListing.objects.exists():
        return
    JobListing.objects.bulk_create(
        [
            JobListing(
                title="Software Engineer — Web Platforms",
                location="Hyderabad, India",
                is_remote=True,
                employment_type="permanent",
                summary=(
                    "Build and maintain web applications and client portals for KYK "
                    "Informatics and our partners. You'll work across the stack, from "
                    "API design to front-end delivery."
                ),
            ),
            JobListing(
                title="AI/ML Engineer",
                location="Remote",
                is_remote=True,
                employment_type="contract",
                summary=(
                    "Help build our generative AI and intelligent automation offerings. "
                    "Experience with LLM integrations, agents, or applied ML is a strong plus."
                ),
            ),
            JobListing(
                title="Technical Recruiter",
                location="Hyderabad, India",
                is_remote=False,
                employment_type="permanent",
                summary=(
                    "Source and screen candidates for our Global Recruitment clients across "
                    "IT and non-IT roles, domestic and international."
                ),
            ),
        ]
    )


def unseed_jobs(apps, schema_editor):
    JobListing = apps.get_model("leads", "JobListing")
    JobListing.objects.filter(
        title__in=[
            "Software Engineer — Web Platforms",
            "AI/ML Engineer",
            "Technical Recruiter",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0002_application"),
    ]

    operations = [
        migrations.RunPython(seed_jobs, unseed_jobs),
    ]

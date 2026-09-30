from django.db import migrations


def seed_content(apps, schema_editor):
    Service = apps.get_model("leads", "Service")
    Post = apps.get_model("leads", "Post")

    if not Service.objects.exists():
        Service.objects.bulk_create(
            [
                Service(
                    title="Global Recruitment",
                    domain="recruitment",
                    icon="🌎",
                    tagline="Right talent. Right opportunity. Right connection.",
                    description=(
                        "IT and non-IT recruitment, contract staffing, permanent hiring, "
                        "and executive search across domestic and international markets."
                    ),
                    order=1,
                ),
                Service(
                    title="Software & Web Development",
                    domain="software",
                    icon="🖥️",
                    tagline="Idea → Design → Develop → Deploy → Improve.",
                    description=(
                        "Custom software, enterprise applications, websites, e-commerce "
                        "platforms, and mobile apps built around real business requirements."
                    ),
                    order=2,
                ),
                Service(
                    title="AI · AGI · ASI",
                    domain="ai",
                    icon="🧠",
                    tagline="Building toward the next generation of intelligence.",
                    description=(
                        "Generative AI, AI agents, intelligent automation today — with "
                        "long-term research into AGI, ASI, and advanced computing."
                    ),
                    order=3,
                ),
            ]
        )

    if not Post.objects.exists():
        Post.objects.create(
            title="Welcome to KYK Informatics",
            slug="welcome-to-kyk-informatics",
            excerpt="A quick look at what we're building across talent, software, and AI.",
            body=(
                "KYK Informatics connects people to opportunity, builds the software "
                "modern businesses run on, and researches the intelligent systems that "
                "come next. This is where we'll share updates on all three.\n\n"
                "Check back here for news on new roles, product launches, and research "
                "milestones as we move toward AGI, ASI, and beyond."
            ),
            is_published=True,
        )


def unseed_content(apps, schema_editor):
    Service = apps.get_model("leads", "Service")
    Post = apps.get_model("leads", "Post")
    Service.objects.filter(
        title__in=["Global Recruitment", "Software & Web Development", "AI · AGI · ASI"]
    ).delete()
    Post.objects.filter(slug="welcome-to-kyk-informatics").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0004_savedjob_service_post"),
    ]

    operations = [
        migrations.RunPython(seed_content, unseed_content),
    ]

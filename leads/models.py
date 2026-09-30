from django.db import models
from django.utils.text import slugify


class Domain(models.TextChoices):
    RECRUITMENT = "recruitment", "Global Recruitment"
    SOFTWARE = "software", "Software & Web Development"
    AI = "ai", "AI · AGI · ASI"
    OTHER = "other", "Something else"


class Lead(models.Model):
    """A contact-form submission from the KYK Technologies website."""

    name = models.CharField(max_length=150)
    email = models.EmailField()
    domain = models.CharField(max_length=20, choices=Domain.choices, default=Domain.OTHER)
    message = models.TextField()

    # Populated automatically by the lightweight interest classifier in leads/utils.py,
    # independent of the domain the visitor selected — useful for routing/QA.
    predicted_domain = models.CharField(max_length=20, choices=Domain.choices, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.get_domain_display()}"


class JobListing(models.Model):
    """Open roles surfaced by the Global Recruitment domain."""

    title = models.CharField(max_length=200)
    location = models.CharField(max_length=150, blank=True)
    is_remote = models.BooleanField(default=False)
    employment_type = models.CharField(
        max_length=40,
        choices=[
            ("contract", "Contract Staffing"),
            ("permanent", "Permanent Hiring"),
            ("executive", "Executive Recruitment"),
        ],
        default="permanent",
    )
    summary = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ApplicationStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    INTERVIEW = "interview", "Interview"
    OFFER = "offer", "Offer"
    REJECTED = "rejected", "Not Selected"


class Application(models.Model):
    """A candidate account's application to one job listing."""

    candidate = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="applications"
    )
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name="applications")
    phone = models.CharField(max_length=30, blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    cover_note = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.SUBMITTED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("candidate", "job")

    def __str__(self):
        return f"{self.candidate} -> {self.job} ({self.status})"


class SavedJob(models.Model):
    """A job a candidate has bookmarked to apply to later."""

    candidate = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="saved_jobs"
    )
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("candidate", "job")

    def __str__(self):
        return f"{self.candidate} saved {self.job}"


class Service(models.Model):
    """A service offering shown on the public Services page, editable by HR/admin."""

    title = models.CharField(max_length=150)
    domain = models.CharField(max_length=20, choices=Domain.choices, default=Domain.OTHER)
    icon = models.CharField(max_length=8, blank=True, help_text="An emoji, e.g. 🤖")
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class Post(models.Model):
    """A blog / insights article, editable by HR/admin."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "post"
            slug = base
            i = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

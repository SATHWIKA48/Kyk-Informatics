import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .forms import ApplicationForm, ProfileForm, SignUpForm
from .models import Application, ApplicationStatus, Domain, JobListing, Lead, Post, SavedJob, Service
from .utils import classify_message


@csrf_exempt
@require_http_methods(["POST"])
def contact_lead(request):
    """
    POST /api/contact/
    Body (JSON): { "name": str, "email": str, "domain": str, "message": str }

    Matches the form fields posted by the KYK Technologies front-end
    (name, email, domain, message).
    """
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    message = (payload.get("message") or "").strip()
    domain_label = (payload.get("domain") or "").strip()

    if not name or not email or not message:
        return JsonResponse(
            {"ok": False, "error": "name, email and message are required."}, status=400
        )

    domain_value = _domain_label_to_value(domain_label)

    lead = Lead.objects.create(
        name=name,
        email=email,
        domain=domain_value,
        message=message,
        predicted_domain=classify_message(message),
    )

    return JsonResponse(
        {
            "ok": True,
            "id": lead.id,
            "predicted_domain": lead.predicted_domain,
            "message": "Thanks — the KYK team will follow up shortly.",
        },
        status=201,
    )


def _domain_label_to_value(label: str) -> str:
    label = label.lower()
    if "recruit" in label:
        return Domain.RECRUITMENT
    if "software" in label or "web" in label:
        return Domain.SOFTWARE
    if "ai" in label or "agi" in label or "asi" in label:
        return Domain.AI
    return Domain.OTHER


@require_http_methods(["GET"])
def job_listings(request):
    """GET /api/jobs/ — active roles for the Global Recruitment domain."""
    jobs = JobListing.objects.filter(is_active=True).values(
        "id", "title", "location", "is_remote", "employment_type", "summary"
    )
    return JsonResponse({"results": list(jobs)})


# ---------------------------------------------------------------------------
# Candidate portal — account sign-up, job browsing, applying, and a dashboard
# that shows each candidate their own applications and status.
# ---------------------------------------------------------------------------

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "portal/signup.html", {"form": form})


def job_list_view(request):
    jobs = JobListing.objects.filter(is_active=True)
    applied_ids = set()
    saved_ids = set()
    if request.user.is_authenticated:
        applied_ids = set(
            Application.objects.filter(candidate=request.user).values_list("job_id", flat=True)
        )
        saved_ids = set(
            SavedJob.objects.filter(candidate=request.user).values_list("job_id", flat=True)
        )
    return render(
        request,
        "portal/jobs.html",
        {"jobs": jobs, "applied_ids": applied_ids, "saved_ids": saved_ids},
    )


def job_detail_view(request, job_id):
    job = get_object_or_404(JobListing, id=job_id, is_active=True)
    already_applied = False
    already_saved = False
    if request.user.is_authenticated:
        already_applied = Application.objects.filter(candidate=request.user, job=job).exists()
        already_saved = SavedJob.objects.filter(candidate=request.user, job=job).exists()
    return render(
        request,
        "portal/job_detail.html",
        {"job": job, "already_applied": already_applied, "already_saved": already_saved},
    )


@login_required
@require_http_methods(["POST"])
def toggle_save_job(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    saved, created = SavedJob.objects.get_or_create(candidate=request.user, job=job)
    if not created:
        saved.delete()
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/jobs/"
    return redirect(next_url)


@login_required
def saved_jobs_view(request):
    saved = SavedJob.objects.filter(candidate=request.user).select_related("job")
    return render(request, "portal/saved_jobs.html", {"saved": saved})


@login_required
def apply_view(request, job_id):
    job = get_object_or_404(JobListing, id=job_id, is_active=True)

    if Application.objects.filter(candidate=request.user, job=job).exists():
        return redirect("dashboard")

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = request.user
            application.job = job
            application.save()
            return redirect("dashboard")
    else:
        form = ApplicationForm()

    return render(request, "portal/apply.html", {"form": form, "job": job})


@login_required
def dashboard_view(request):
    applications = Application.objects.filter(candidate=request.user).select_related("job")
    return render(request, "portal/dashboard.html", {"applications": applications})


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "portal/profile.html", {"form": form})


# ---------------------------------------------------------------------------
# Public content — Services and Insights (blog), both managed from /admin/
# ---------------------------------------------------------------------------

def service_list_view(request):
    services = Service.objects.filter(is_active=True)
    return render(request, "portal/services.html", {"services": services})


def post_list_view(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "portal/insights_list.html", {"posts": posts})


def post_detail_view(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, "portal/insights_detail.html", {"post": post})


# ---------------------------------------------------------------------------
# HR / staff analytics dashboard
# ---------------------------------------------------------------------------

@staff_member_required
def hr_analytics_view(request):
    leads_by_domain = Lead.objects.values("domain").annotate(count=Count("id")).order_by("-count")
    applications_by_status = (
        Application.objects.values("status").annotate(count=Count("id")).order_by("-count")
    )
    status_labels = dict(ApplicationStatus.choices)
    domain_labels = dict(Domain.choices)

    context = {
        "total_leads": Lead.objects.count(),
        "total_applications": Application.objects.count(),
        "total_candidates": Application.objects.values("candidate").distinct().count(),
        "active_jobs": JobListing.objects.filter(is_active=True).count(),
        "leads_by_domain": [
            {"label": domain_labels.get(row["domain"], row["domain"]), "count": row["count"]}
            for row in leads_by_domain
        ],
        "applications_by_status": [
            {"label": status_labels.get(row["status"], row["status"]), "count": row["count"]}
            for row in applications_by_status
        ],
    }
    return render(request, "portal/hr_analytics.html", context)
# KYK_ASSISTANT_SYSTEM_PROMPT = """You are the website assistant for KYK Informatics \ ("Key to Your Kognitio"), a company working across three domains:
# 1. Global Recruitment — IT and non-IT recruitment, contract staffing, permanent \
# hiring, executive search, across domestic and international markets.
# 2. Software & Web Development — custom software, enterprise applications, \
# websites, e-commerce platforms, mobile apps, API development, cloud solutions.
# 3. AI · AGI · ASI — generative AI, AI agents, intelligent automation today, with \
# long-term research into AGI, ASI, quantum computing, and advanced intelligent systems.

# Answer visitor questions about KYK's services, open roles, and how to engage with \
# the company. For open roles, tell them to check the Careers page (/jobs/). For \
# business inquiries or anything you're unsure about, point them to the contact form. \
# Keep answers brief, friendly, and specific to KYK — you are not a general-purpose \
# assistant and should redirect off-topic questions back to what KYK can help with."""
# ---------------------------------------------------------------------------
# Website assistant — answers visitor questions from KYK's own content
# (jobs and services from the database, plus fixed company info).
# It needs NO external API and NO API key.
# ---------------------------------------------------------------------------

KYK_CONTACT_EMAIL = getattr(settings, "KYK_CONTACT_EMAIL", "hello@kykinformatics.com")

_KYK_FALLBACK_SERVICES = [
    "Global Recruitment — IT and non-IT hiring, contract and permanent staffing, executive search",
    "Software & Web Development — custom software, websites, web and mobile apps, integrations",
    "AI · AGI · ASI — generative AI, AI agents and intelligent automation, plus long-term research",
]


def _kyk_answer(question, jobs, services):
    import re

    t = " " + re.sub(r"[^a-z0-9\s]", " ", (question or "").lower()) + " "
    words = t.split()

    def has(*keys):
        for k in keys:
            if " " in k:
                if k in t:
                    return True
            elif len(k) <= 3:
                if k in words:
                    return True
            elif any(w.startswith(k) for w in words):
                return True
        return False

    if len(words) <= 3 and has("hi", "hello", "hey", "hii", "namaste"):
        return (
            "Hello! I can tell you about KYK's services, current job openings, "
            "how to apply, or how to contact us. What would you like to know?"
        )

    if has("thanks", "thank", "thx"):
        return "You're welcome! Ask me anything else about KYK."

    if has("apply", "application") and not has("status", "track"):
        return (
            "To apply for a role:\n"
            "1. Create an account at /accounts/signup/ (or sign in at /accounts/login/).\n"
            "2. Open a role from /jobs/ and click Apply.\n"
            "3. Add your phone number, resume and a short note.\n"
            "Then track your application status on your dashboard at /dashboard/."
        )

    if has("status", "track", "dashboard"):
        return (
            "Sign in and open your dashboard at /dashboard/. Every application shows "
            "its current status: Submitted, Under Review, Interview, Offer or Not Selected."
        )

    if has("sign up", "signup", "register", "login", "log in", "sign in",
           "password", "account", "profile"):
        return (
            "Create a free candidate account at /accounts/signup/ or sign in at "
            "/accounts/login/. Forgot your password? Use /accounts/password-reset/. "
            "Once signed in you can apply to roles, save jobs, and edit your profile "
            "at /accounts/profile/."
        )

    if has("save", "saved", "bookmark"):
        return (
            "When you're signed in, use the Save button on any role at /jobs/ to "
            "bookmark it. Your saved roles are listed at /saved-jobs/."
        )

    if has("job", "role", "career", "opening", "vacanc", "position", "hiring",
           "internship", "employ", "join"):
        if jobs:
            lines = []
            for j in jobs:
                bits = [j["type"]]
                if j["location"]:
                    bits.append(j["location"])
                if j["remote"]:
                    bits.append("Remote")
                lines.append("• %s — %s" % (j["title"], ", ".join(bits)))
            return (
                "Our current openings:\n" + "\n".join(lines)
                + "\n\nSee full details and apply at /jobs/."
            )
        return (
            "There are no open roles listed right now. Please check /jobs/ again "
            "soon, or send us your details through the contact form."
        )

    if has("recruit", "staffing", "talent", "hire", "headhunt", "executive search", "manpower"):
        return (
            "Our Global Recruitment team helps organizations hire across domestic and "
            "international markets: IT and non-IT roles, contract staffing, permanent "
            "hiring, executive search, candidate sourcing and screening. Tell us what "
            "you need through the contact form on the homepage (/#contact)."
        )

    if has("software", "web", "website", "app", "apps", "mobile", "android", "ios",
           "saas", "api", "cloud", "ecommerce", "e commerce", "develop", "erp", "portal"):
        return (
            "KYK builds software around real business requirements: custom software, "
            "enterprise and business applications, websites and web apps, e-commerce "
            "platforms, Android and iOS apps, API development, system integration and "
            "cloud solutions. Share your idea through the contact form (/#contact)."
        )

    if has("ai", "agi", "asi", "artificial", "machine learning", "ml", "chatbot",
           "generative", "automation", "quantum", "intelligen", "llm"):
        return (
            "On AI, we work today with generative AI, AI agents, machine learning and "
            "intelligent automation. Our longer-term research direction covers AGI, ASI, "
            "quantum computing and human-AI collaboration. Reach out through the contact "
            "form (/#contact) to discuss a project."
        )

    if has("service", "offer", "what do you do", "what does kyk do", "what do",
           "products", "solution", "capabilit", "domain"):
        items = [
            "• " + s["title"] + (" — " + s["tagline"] if s["tagline"] else "")
            for s in services
        ] or ["• " + s for s in _KYK_FALLBACK_SERVICES]
        return "Here's what we offer:\n" + "\n".join(items) + "\n\nSee more at /services/."

    if has("contact", "email", "mail", "phone", "call", "reach", "touch", "address",
           "location", "office", "talk", "consult", "quote", "pricing", "price",
           "cost", "demo", "meeting"):
        return (
            "You can reach us through the contact form on the homepage (/#contact) or "
            "by email at %s. Tell us whether it's about recruitment, software or AI and "
            "the right team will follow up." % KYK_CONTACT_EMAIL
        )

    if has("blog", "insight", "news", "article"):
        return "Read our latest notes and updates at /insights/."

    if has("about", "who are you", "who is", "company", "kyk", "kognitio", "vision",
           "mission", "value", "team", "founder"):
        return (
            "KYK Informatics (\"Key to Your Kognitio\") connects people to opportunity, "
            "builds software and web platforms, and researches AI, AGI and ASI. Our "
            "vision is to be a globally recognized technology organization that connects "
            "talent, technology and intelligence. See the About section on the homepage "
            "(/#about)."
        )

    return (
        "I can help with open roles and how to apply, our services (recruitment, "
        "software and web development, AI), and how to contact us. Try asking: "
        "\"What roles are open?\" or \"What services do you offer?\""
    )


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    last_user = ""
    for m in reversed(payload.get("messages") or []):
        if isinstance(m, dict) and m.get("role") == "user":
            last_user = str(m.get("content", ""))
            break

    if not last_user.strip():
        return JsonResponse({"ok": False, "error": "Please type a question."}, status=400)

    jobs = [
        {
            "title": j.title,
            "type": j.get_employment_type_display(),
            "location": j.location,
            "remote": j.is_remote,
        }
        for j in JobListing.objects.filter(is_active=True)[:8]
    ]
    services = [
        {"title": s.title, "tagline": s.tagline}
        for s in Service.objects.filter(is_active=True)[:8]
    ]

    return JsonResponse({"ok": True, "reply": _kyk_answer(last_user, jobs, services)})


# @csrf_exempt
# @require_http_methods(["POST"])
# def chat_api(request):
#     if not settings.ANTHROPIC_API_KEY:
#         return JsonResponse(
#             {
#                 "ok": False,
#                 "error": (
#                     "The AI assistant isn't configured yet — set the ANTHROPIC_API_KEY "
#                     "environment variable and restart the server."
#                 ),
#             },
#             status=503,
#         )

#     try:
#         payload = json.loads(request.body or "{}")
#     except json.JSONDecodeError:
#         return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

#     messages = payload.get("messages") or []
#     if not messages:
#         return JsonResponse({"ok": False, "error": "messages is required."}, status=400)

#     try:
#         import anthropic
#     except ImportError:
#         return JsonResponse(
#             {"ok": False, "error": "The 'anthropic' package isn't installed — run: pip install anthropic"},
#             status=500,
#         )

#     try:
#         client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
#         response = client.messages.create(
#             model=settings.ANTHROPIC_MODEL,
#             max_tokens=500,
#             system=KYK_ASSISTANT_SYSTEM_PROMPT,
#             messages=messages,
#         )
#         reply_text = "".join(
#             block.text for block in response.content if getattr(block, "type", None) == "text"
#         )
#     except Exception as exc:  # noqa: BLE001
#         return JsonResponse({"ok": False, "error": str(exc)}, status=502)

#     return JsonResponse({"ok": True, "reply": reply_text})

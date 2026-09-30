# KYK Technologies — Django Backend

This is the backend for the KYK Technologies website. It serves the site
(`templates/index.html`, the same animated page you were shown in chat) and
exposes a small JSON API that the site's contact form talks to.

## What's included

- `config/` — Django project (settings, URLs, WSGI/ASGI)
- `leads/` — app with two models:
  - `Lead` — contact-form submissions, with a lightweight keyword-based
    classifier (`leads/utils.py`) that guesses which KYK domain
    (Recruitment / Software / AI) a message is really about
  - `JobListing` — open roles for the Global Recruitment domain
- `templates/index.html` — the animated front-end, served at `/`
- `leads/urls.py` — API routes:
  - `POST /api/contact/` — create a lead from the contact form
  - `GET /api/jobs/` — list active job listings

## Run it locally — the easy way

You need Python 3 installed first (https://www.python.org/downloads/ — on
Windows, tick "Add Python to PATH" during install). That's the one step that
can't be automated.

After that, run one script and everything else — virtual environment,
installing Django, setting up the database, starting the server — happens
for you:

- **Mac/Linux:** open a terminal in this folder and run `bash setup.sh`
- **Windows:** double-click `setup.bat` (or run it from Command Prompt)

When it finishes, open **http://127.0.0.1:8000/** — that's the full animated
site, with the contact form posting live to `/api/contact/`.

To see submitted leads, stop the server (Ctrl+C) and run:
```
python manage.py createsuperuser
```
then start it again (`python manage.py runserver` — no need to re-run the
setup script) and visit **http://127.0.0.1:8000/admin/**.

## Run it locally — the manual way

If you'd rather run each step yourself instead of using the script:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

## Candidate portal (new)

Job seekers can now create an account, browse open roles, apply, and track
their application status:

- `/accounts/signup/` — create an account (name, email, username, password)
- `/accounts/login/` / `/accounts/logout/`
- `/accounts/password-reset/` — forgot-password flow; in dev, the reset
  email is printed to the terminal (not actually sent) via Django's console
  email backend — look for the link inside it
- `/accounts/profile/` — a signed-in candidate can view/edit their name and
  email (username can't be changed here)
- `/jobs/` — browse active job listings (three sample roles are seeded on
  first `migrate`)
- `/jobs/<id>/` — view a role and apply
- `/jobs/<id>/apply/` — application form (phone, resume upload, cover note)
- `/jobs/<id>/save/` — save/unsave a role (POST-only toggle)
- `/saved-jobs/` — a candidate's bookmarked roles
- `/dashboard/` — a signed-in candidate's own applications and their status

The site's nav bar (`templates/index.html`) now links to `/jobs/` (Careers)
and `/accounts/login/` (Sign in).

**Updating a candidate's status:** go to `/admin/`, open **Applications**,
and change the `status` field (Submitted → Under Review → Interview → Offer
/ Not Selected) — it's editable right from the list view. The candidate
sees the update immediately next time they open their dashboard, **and now
gets an emailed notification too** (see below).

**Resume uploads** are saved under `media/resumes/`. In production, don't
rely on local disk storage — point `DEFAULT_FILE_STORAGE` at S3 or another
object store, since most hosts wipe local files on redeploy.

## Django Admin / HR (new)

Beyond the Leads and Applications already in `/admin/`, HR/staff can now
manage:

- **Candidate Management** — `/admin/auth/user/` now shows an
  "Applications" column per user, so staff can see engagement at a glance
  without a separate model.
- **Blog / Insights Management** — `/admin/leads/post/`. Public pages at
  `/insights/` (list) and `/insights/<slug>/` (detail). Slugs
  auto-generate from the title.
- **Service Management** — `/admin/leads/service/`. Public page at
  `/services/`. Each service has a title, an optional emoji icon, a
  tagline, a description, a domain tag, and a display order.
- **HR Analytics dashboard** — `/hr/analytics/` (staff-only). A quick
  snapshot: total leads, candidates, applications, active jobs, leads by
  domain, and applications by status. It's deliberately simple — for
  deeper reporting, use `/admin/` directly or query the database.

## Advanced features — what's built, what's next

Two Phase 5 items are included:

- **Email notifications** (`leads/signals.py`) — when a staff member
  changes an `Application`'s status in `/admin/`, the candidate is
  automatically emailed (via whatever `EMAIL_BACKEND` is configured — the
  console backend in dev, real SMTP in production).
- **Analytics dashboard** — see `/hr/analytics/` above.

The rest of Phase 5 — an AI chatbot, resume parsing, job recommendations,
interview scheduling, and a client portal — are each substantial features
in their own right (new integrations, new data models, and in the chatbot's
case, an LLM API key and ongoing usage cost), so they're intentionally left
for a follow-up build rather than bolted on quickly here. A reasonable
order to tackle them:

1. **Resume parsing** — extract text from uploaded resumes (e.g. with
   `pdfplumber`/`python-docx`) to auto-fill candidate skills/experience.
2. **Job recommendations** — use parsed resume data (or just candidate
   history) to rank `/jobs/` by fit.
3. **Interview scheduling** — a simple available-slots model plus a booking
   view is enough to start; a full calendar sync (Google Calendar/Outlook)
   is a bigger follow-up.
4. **Client portal** — mirrors the candidate portal, but for companies
   submitting hiring/project requests and viewing their own leads' status.
5. **AI chatbot** — a widget on the public site backed by the Anthropic
   API, answering questions about services/roles from your own content.

## Notes for deployment


- Set `KYK_DEBUG=0` and a real `KYK_SECRET_KEY` environment variable in
  production.
- Set a real `KYK_EMAIL_BACKEND` (e.g. `django.core.mail.backends.smtp.EmailBackend`)
  plus your SMTP/SES/SendGrid credentials so password-reset emails actually
  send — the default console backend only works for local testing.
- Set `KYK_ALLOWED_HOSTS` to your real domain(s), e.g.
  `KYK_ALLOWED_HOSTS=kyktechnologies.com,www.kyktechnologies.com`.
- Swap the `DATABASES` setting in `config/settings.py` for Postgres (or
  another production database) when you're ready — SQLite is fine for
  development only.
- The contact endpoint is currently `@csrf_exempt` for simplicity, since it's
  called from static/fetch JS. If you serve the form from the same Django
  templates and want CSRF protection, switch to Django's CSRF token pattern
  instead.
- `leads/utils.py` uses a simple keyword classifier to route leads. Swap in a
  call to an LLM there (e.g. the Anthropic API) if you want smarter,
  free-text domain classification later.

## Extending the AI-animated frontend

`templates/index.html` is self-contained HTML/CSS/JS: a canvas-based neural
network animates behind the hero, a concentric-rings canvas visualizes the
AI → AGI → ASI tiers, and the technology roadmap draws itself in as you
scroll. Add Django template tags (`{{ }}` / `{% %}`) inside it to make any
part — job listings, testimonials, blog posts — dynamic and database-backed.

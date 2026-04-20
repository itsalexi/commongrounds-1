# Common Grounds — CLAUDE.md

## Project Overview

Django 6.0.2 community platform with six feature apps: accounts, bookclub, commissions, diyprojects, localevents, and merchstore. Uses Tailwind CSS 4 via `django-tailwind`. SQLite3 database. Python 3.14.

## Repository Layout

```
commongrounds-1/
├── commongrounds/          # Django project root (run all commands from here)
│   ├── commongrounds/      # Project config (settings.py, urls.py)
│   ├── accounts/           # Auth, user profiles, role-based access
│   ├── bookclub/           # Books and genres
│   ├── commissions/        # Commission requests
│   ├── diyprojects/        # DIY project guides
│   ├── localevents/        # Local events
│   ├── merchstore/         # Product catalog
│   ├── theme/              # Tailwind CSS app (static_src → static/css/dist)
│   ├── templates/          # Project-wide templates (base.html, auth)
│   ├── manage.py
│   └── Procfile.tailwind   # Honcho: runs Django + Tailwind watcher
├── lectures/               # Course materials (not part of the app)
└── myenv/                  # Python venv (gitignored)
```

## Development Commands

All commands run from `commongrounds/` (the directory containing `manage.py`).

```bash
# Start dev server only
python manage.py runserver

# Start Django + Tailwind CSS watcher together (recommended)
honcho -f Procfile.tailwind start

# Database
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser

# Tests
python manage.py test
python manage.py test <app_name>

# Build Tailwind CSS once
python manage.py tailwind build
```

## Environment Variables

Copy `.env.example` (or create `.env`) in `commongrounds/`:

```
SECRET_KEY='...'
DEBUG=True
```

## Architecture Patterns

### Models
Each app follows the same pattern: a category/type model + a main content model with a ForeignKey to it. All content models include `created_on` / `updated_on` timestamps.

### Role-Based Access
`accounts` defines five roles via `Profile.Role` TextChoices:
- `MARKET_SELLER`, `EVENT_ORGANIZER`, `BOOK_CONTRIBUTOR`, `PROJECT_CREATOR`, `COMMISSION_MAKER`

Use `@role_required(role)` decorator (FBVs) or `RoleRequiredMixin` (CBVs) to restrict views.

### URL Namespacing
Each app has its own `urls.py` included under its app name prefix:
- `/accounts/`, `/bookclub/`, `/commissions/`, `/diyprojects/`, `/localevents/`, `/merchstore/`

### Templates
Extend `base.html`. Available blocks: `title`, `header`, `content`, `styles`, `scripts`.

Tailwind classes are scanned from `theme/static_src/**/*.{html,py,js}` — add new paths there if needed.

## Admin

All models are registered. Inlines: Profile under User, Commission under CommissionType, Product under ProductType. Access at `/admin/`.

## Known Gaps / Watch-Outs

- Tests exist as empty stubs — write real tests before shipping features.
- `ALLOWED_HOSTS` is empty — must be set for any non-localhost deployment.
- SQLite3 only — not suitable for production; migrate to PostgreSQL when deploying.
- Compiled Tailwind CSS (`theme/static/css/dist/styles.css`) is gitignored — run `tailwind build` after checkout.

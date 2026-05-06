# Common Grounds — AGENTS.md

Agent-oriented guide. Read CLAUDE.md first for full project context.

## Quick Reference

| Item | Value |
|------|-------|
| Framework | Django 6.0.2 |
| Python | 3.14 |
| Database | SQLite3 (`commongrounds/db.sqlite3`) |
| CSS | Tailwind CSS 4 (`django-tailwind`) |
| Working directory | `commongrounds/` (contains `manage.py`) |
| Venv | `myenv/` at repo root |

## Before You Start

```bash
# Activate venv
source myenv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations
cd commongrounds
python manage.py migrate

# Build Tailwind (CSS is gitignored)
python manage.py tailwind build
```

## Adding a New Feature App

1. `python manage.py startapp <name>` inside `commongrounds/`
2. Add to `INSTALLED_APPS` in `commongrounds/settings.py`
3. Create `<name>/urls.py` and include it in `commongrounds/urls.py`
4. Follow the existing pattern: category/type model + content model with FK, `created_on`/`updated_on` fields
5. Register models in `<name>/admin.py`
6. Templates go in `<name>/templates/<name>/`

## Adding a View

- FBVs: use `@login_required` + `@role_required(Profile.Role.<ROLE>)` for protected routes
- CBVs: inherit from `LoginRequiredMixin` + `RoleRequiredMixin` (both in `accounts/`)
- Map in the app's `urls.py`

## Template Conventions

```html
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block content %}
  <!-- content here -->
{% endblock %}
```

Do not add `{% load tailwind_tags %}` to child templates — it's in `base.html`.

## Data Models Reference

| App | Models |
|-----|--------|
| accounts | `Profile` (1-to-1 User, role field) |
| bookclub | `Genre`, `Book` |
| commissions | `CommissionType`, `Commission` |
| diyprojects | `ProjectCategory`, `Project` |
| localevents | `EventType`, `Event` |
| merchstore | `ProductType`, `Product` |

## Testing

Tests live in `<app>/tests.py`. Currently stubs only — all are safe to overwrite.

```bash
python manage.py test                    # all
python manage.py test <app>              # single app
python manage.py test <app>.<TestClass>  # single class
```

Use `django.test.TestCase` for DB tests, `SimpleTestCase` for pure logic.

## Common Pitfalls

- **Tailwind not loading**: run `python manage.py tailwind build` — the compiled CSS is gitignored.
- **Migration conflicts**: run `python manage.py migrate --run-syncdb` only as a last resort; prefer `makemigrations`.
- **Role check failures**: `Profile` is created via a post-save signal — never assume `request.user.profile` exists without a `try/except` on first login.
- **Static files missing**: run `python manage.py collectstatic` before any non-debug deployment.

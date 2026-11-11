# Lab 5: Server-Side Template Injection with Information Disclosure via User-Supplied Objects

**Category:** Server-Side Template Injection (SSTI)
**Difficulty:** Practitioner
**Lab link:** [SSTI with information disclosure via user-supplied objects](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-with-information-disclosure-via-user-supplied-objects)

## Overview

The CMS product template editor injects user input into a Django template. Django's template engine is deliberately restricted — it doesn't execute arbitrary Python expressions — but framework objects passed into the template context (including `settings`) are accessible. `settings.SECRET_KEY` leaks the Django secret key, which is the lab goal.

**Engine:** Django (Python)

## Key Concepts

- **Django template language (DTL) is not Python:** `{{7*7}}` renders as the string `{{7*7}}`, not `49`. Arithmetic expressions are not evaluated. This distinguishes Django from Jinja2/FreeMarker/Tornado.
- **`{% debug %}`:** Django-specific tag that dumps all variables and filters available in the current template context — useful for discovery.
- **Context object access:** template variables passed to `render()` are accessible by dot notation. If `settings` is passed (or accessible via an object in context), `{{settings.SECRET_KEY}}` reads it directly.
- **Goal is information disclosure, not RCE:** Django's DTL sandbox prevents `import`, `eval`, and direct function calls, so this lab demonstrates that SSTI doesn't always mean code execution — sometimes secrets are enough.

## Solution

### Step 1 — Log in and find the injection point

Credentials: `content-manager` / `C0nt3ntM4n4g3r`. Navigate to a product → **Edit template**.

### Step 2 — Fingerprint the engine

Add `{{7*7}}` to the template. If it renders literally (not `49`) → Django DTL (not Jinja2).

Confirm with:
```django
{% debug %}
```
This dumps all context variables, confirming Django and revealing what objects are available.

### Step 3 — Leak the secret key

```django
{{settings.SECRET_KEY}}
```

The secret key renders in the page response. Copy it.

### Step 4 — Submit

Click **Submit solution** on the lab page and paste the secret key. Lab solved.

## Why `settings` Is Accessible

Django passes a `settings` object (or an object that exposes it) into some template contexts, particularly in admin and CMS-style views. The lab's template context includes it directly, making `{{settings.SECRET_KEY}}` a valid expression.

## Django DTL vs Jinja2

| Feature | Django DTL | Jinja2 |
|---|---|---|
| `{{7*7}}` | renders literally | `49` |
| `{% for %}` | supported | supported |
| `{% import %}` | not supported | not supported |
| Arbitrary Python | blocked | blocked (by default) |
| Object attribute access | dot notation | dot notation |

## Why SECRET_KEY Matters

Django uses `SECRET_KEY` to sign:
- Session cookies (forge any user's session)
- CSRF tokens
- Password reset tokens
- Any `django.core.signing` data

Knowing it allows full session forgery and account takeover.

## Remediation

- Never pass `settings` or other sensitive framework objects into template context.
- Use `{% autoescape on %}` and restrict context to only the data the template actually needs.
- Consider switching to Jinja2 with `sandbox=True` for user-editable templates, or use a logic-less engine entirely.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/server-side-template-injection/lab-05-django-info-disclosure/solve.py)

Logs in as content-manager, injects `{{settings.SECRET_KEY}}` into a product template, reads the key from the response, and submits it.

## Key Takeaways

- Django DTL blocks code execution but object attribute traversal still works — `{{settings.SECRET_KEY}}` is valid.
- `{% debug %}` is a free recon primitive in Django templates.
- SSTI impact isn't always RCE — a leaked `SECRET_KEY` is full compromise via session forgery.
- Identify Django by `{{7*7}}` rendering literally and by `{% debug %}` working.

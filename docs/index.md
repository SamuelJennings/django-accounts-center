# Django Accounts Center

The account-management layer for [django-mvp](https://github.com/SamuelJennings/django-mvp)
projects. It gives a signed-in user one place to manage their account, and gives you a way to put
more things there as the project grows.

This package is not usable on its own. It renders on the django-mvp app shell (DaisyUI 5 +
Tailwind CSS v4 + django-cotton) and expects it.

## What it provides

- **An entrance layout.** Sign-in, sign-up and recovery pages render as a centered card with your
  site logo, outside the app shell.
- **An Account Center.** A management layout, a sub menu, and an overview page whose cards come
  from whatever you have installed.
- **An integration system.** The machinery that lets a third-party app add its own
  account-management pages to that Account Center.

## Integrations

An integration is a gated sub-app that teaches the Account Center about one third-party package.
You enable one by adding it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = ["dac", "dac.allauth", ...]
```

From there the integration contributes its own labelled menu group, any overview cards it needs,
and its template overrides. What is installed decides which contributions exist.

Because every integration is gated, a project carries only the dependencies of the integrations it
turns on. Shipped today: `dac.allauth`, and it is the only one.

## Installation

```bash
pip install django-accounts-center[allauth]
```

Settings, URLs and customisation are covered in the
[README](https://github.com/django-mvp/django-accounts-center#installation).

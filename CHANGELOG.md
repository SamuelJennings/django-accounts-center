# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Dependency constraints now match what is verified. Django widens to
  `>=5.2,<7.0`, which is the range CI tests — the previous `<6.0` cap declared
  an install that pip would refuse while two green Django 6.0 checks said
  otherwise. `django-mvp` gains bounds (`>=0.15,<1.0`); it was previously
  unconstrained despite this package depending on its internals. The `allauth`
  extra pins to the major it is coupled to (`>=65.18,<66.0`), with matching
  caps on crispy-forms and crispy-tailwind.

### Fixed

- The test URL configuration mounted `allauth.urls` alongside `dac.urls`, which
  already includes it. Every allauth URL name was registered twice and resolved
  by last registration.

## [0.7.0]

Releases before this file existed are recorded in the
[GitHub releases](https://github.com/django-mvp/django-accounts-center/releases).

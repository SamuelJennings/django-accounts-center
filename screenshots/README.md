# screenshots/

This directory contains **screenshot-only pytest-playwright test modules** that generate visual documentation artifacts.

## Why a separate directory?

`pyproject.toml` sets `testpaths = ["tests"]`, so a plain `pytest` invocation never discovers this directory. This keeps normal test runs fast. Screenshot tests are slow by nature (they spin up a live server and a headless browser) and only need to run when UI changes.

## Running screenshot tests

```powershell
poetry run pytest screenshots/
```

To regenerate screenshots for a specific module:

```powershell
poetry run pytest screenshots/test_signup_screenshots.py
```

## Output

Generated screenshots are saved under `docs/_static/` partitioned by viewport tier:

```
docs/_static/
├── desktop/    # 1440×900
├── tablet/     # 768×1024
└── mobile/     # 390×844
```

Screenshots are **living documentation** — they must be committed alongside any UI change and must be kept up to date. A PR that modifies UI without updated screenshots must not be merged.

## Contents

| File | Page | Permutations |
|------|------|-------------|
| `test_signup_screenshots.py` | Signup page (`/account-center/signup/`) and passkey signup page (`/account-center/signup/passkey/`) | 6 settings permutations × 3 viewports = 18 files |

# Django Account Center

## Installation

```
pip install django-account-management
```

add `account_management` to your `INSTALLED_APPS` in `settings.py`

```python
INSTALLED_APPS = [
    ...
    "account_management",
    "flex_menu",
    "easy_icons",
    ...
]
```

## Theme Templates

All templates that allow you to customise the look and feel of you Account Center are located under cotton/dac/ directory. You can override these templates in your own project by copying them to your templates directory.




## Menus

`django-account-management` registers two menus with `django-flex-menu` that you can add to or modify in order to customize your account management experience.

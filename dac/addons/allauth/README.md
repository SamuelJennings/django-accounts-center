# Django-Allauth Integration with DAC

This integration provides seamless styling of django-allauth templates using the Django Accounts Center (DAC) components and layouts.

## Overview

The integration works by overriding allauth's layout and element templates to use DAC's component system, providing a consistent look and feel across your entire application.

## Integration Components

### 1. Layouts

#### Base Layout (`allauth/layouts/base.html`)
- Extends `dac/base.html` 
- Provides common structure for all allauth pages
- Includes DAC navigation and styling

#### Entrance Layout (`allauth/layouts/entrance.html`)
- Used for authentication pages (login, signup, password reset)
- Centers content with professional form styling
- Includes message handling with proper styling

#### Management Layout (`allauth/layouts/manage.html`)
- Used for account management pages (change password, email management)
- Extends DAC dashboard layout
- Integrates with DAC card components

### 2. Elements Integration

#### Form Elements
- **Button** → `c-dac.action`: Maps submit buttons to primary style, others to secondary
- **Panel** → `c-dac.card`: Account panels use DAC card components
- **Field** → Styled form fields: Proper Tailwind styling with validation states
- **Form** → Structured forms: Consistent spacing and layout

#### UI Elements  
- **Alert** → DAC alerts: Color-coded messages with icons
- **Badge** → `c-dac.components.badge`: Status indicators
- **Provider** → Social login buttons using `c-dac.action`

#### Typography
- **H1/H2** → Consistent heading styles matching DAC design
- **P** → Styled paragraphs with proper text colors
- **HR** → Styled dividers with "or" text for form sections

## Usage Examples

### Basic Login Template
```django-html
{% extends "allauth/layouts/entrance.html" %}
{% load allauth i18n %}

{% block entrance_title %}
  {% trans "Sign in to your account" %}
{% endblock %}

{% block entrance_content %}
  {% element form method="post" action=action_url %}
    {% slot body %}
      {% csrf_token %}
      {% element field type="email" name="login" required=True %}
        {% slot label %}{% trans "Email" %}{% endslot %}
      {% endelement %}
      {% element field type="password" name="password" required=True %}
        {% slot label %}{% trans "Password" %}{% endslot %}
      {% endelement %}
    {% endslot %}
    {% slot actions %}
      {% element button type="submit" %}{% trans "Sign In" %}{% endelement %}
    {% endslot %}
  {% endelement %}
{% endblock %}
```

### Account Management Template
```django-html
{% extends "allauth/layouts/manage.html" %}
{% load allauth i18n %}

{% block manage_title %}{% trans "Email Management" %}{% endblock %}

{% block content %}
  {% element panel %}
    {% slot title %}{% trans "Your Email Addresses" %}{% endslot %}
    {% slot body %}
      <!-- Email management content -->
    {% endslot %}
    {% slot actions %}
      {% element button type="submit" %}{% trans "Save" %}{% endelement %}
    {% endslot %}
  {% endelement %}
{% endblock %}
```

## Styling Customization

### Color Mapping
- **Primary actions**: Blue (`primary-600`)
- **Secondary actions**: Gray (`gray-600`) 
- **Success**: Green (`green-600`)
- **Warning**: Yellow (`yellow-600`)
- **Error/Danger**: Red (`red-600`)

### Form Field Styling
All form fields automatically receive:
- Consistent padding and borders
- Focus states with primary color
- Error states with red styling
- Proper spacing and typography

### Message/Alert Styling
- Success: Green background with check icon
- Warning: Yellow background with warning icon  
- Error: Red background with X icon
- Info: Blue background with info icon

## Template Overrides

To customize specific pages, create templates in your app following this structure:

```
your_app/templates/
├── account/
│   ├── login.html
│   ├── signup.html  
│   ├── password_change.html
│   └── email.html
├── socialaccount/
│   └── connections.html
└── allauth/
    ├── layouts/
    │   ├── base.html      (customize overall layout)
    │   ├── entrance.html  (customize auth pages)
    │   └── manage.html    (customize management pages)
    └── elements/
        ├── button.html    (customize buttons)
        ├── field.html     (customize form fields)
        └── alert.html     (customize messages)
```

## Benefits

1. **Consistency**: All allauth pages match your DAC design system
2. **Maintainability**: Style changes in DAC automatically apply to allauth
3. **Responsiveness**: All templates work seamlessly on mobile and desktop
4. **Accessibility**: Proper ARIA labels and semantic markup
5. **Performance**: Leverages DAC's optimized CSS and JavaScript

## Configuration

Ensure your Django settings include:

```python
INSTALLED_APPS = [
    'dac.addons.allauth',  # Before 'allauth'
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... other apps
]

TEMPLATES = [
    {
        'DIRS': [
            # Your template directories
        ],
        'APP_DIRS': True,  # This allows finding DAC allauth templates
        # ... other settings
    }
]
```

This integration provides a professional, cohesive authentication experience that matches your DAC application design.

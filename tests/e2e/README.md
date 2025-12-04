# E2E Testing for Django Accounts Center

This directory contains end-to-end tests for the django-accounts-center package using Playwright.

## Setup

### 1. Install Dependencies

First, install the required dependencies:

```powershell
poetry install
```

### 2. Install Playwright Browsers

After installing dependencies, you need to install the Playwright browsers:

```powershell
poetry run playwright install
```

This will download Chromium, Firefox, and WebKit browsers for testing.

## Running the Tests

### Run All E2E Tests

```powershell
poetry run pytest tests/e2e/ -v
```

### Run Specific Test File

```powershell
poetry run pytest tests/e2e/test_e2e_login_flow.py -v
```

### Run Tests with Screenshots

Screenshots are automatically captured during test execution and saved to `screenshots/e2e/` directory.

### Run Tests in Headed Mode (Visual Browser)

To see the browser during test execution:

```powershell
poetry run pytest tests/e2e/ --headed
```

### Run Tests with Slow Motion

To slow down test execution for debugging:

```powershell
poetry run pytest tests/e2e/ --slowmo 1000
```

## Test Structure

### Test Files

- **`test_e2e_login_flow.py`** - Login functionality tests
  - Standard email/password login
  - Form validation and errors
  - Redirect behavior
  - Responsive design (desktop/tablet/mobile)
  - Form interactions and UX

- **`test_e2e_dashboard.py`** - Dashboard functionality tests
  - Dashboard loading and authentication
  - Status cards display
  - User-specific data
  - Security warnings
  - Quick actions
  - Responsive layouts

- **`test_e2e_password_reset.py`** - Password reset workflow tests
  - Forgot password flow
  - Email confirmation
  - Password reset form
  - Validation errors
  - Security features

- **`test_e2e_navigation.py`** - Navigation and menu tests
  - Sidebar navigation (desktop)
  - Mobile offcanvas menu
  - Logout flow
  - Unauthorized access redirects
  - Navigation consistency

- **`test_e2e_signup_flow.py`** - Signup/registration tests
  - Registration form
  - Form validation
  - Email verification workflow
  - First-time dashboard access
  - Mobile responsive design

### Fixtures and Utilities (`conftest.py`)

The `conftest.py` file provides:

- **Viewport Fixtures**: `page_desktop`, `page_tablet`, `page_mobile`, `page_all_viewports`
- **User Fixtures**: `e2e_user`, `e2e_unverified_user`
- **Helper Functions**:
  - `login_user()` - Programmatically log in a user
  - `logout_user()` - Log out a user via UI
  - `check_entrance_layout()` - Verify entrance layout is used
  - `check_standard_layout()` - Verify standard layout is used
  - `get_email_verification_url()` - Extract verification URL from email
  - `get_password_reset_url()` - Extract password reset URL from email
  - `verify_alert_message()` - Check alert messages
  - `take_screenshot()` - Capture screenshots
- **Screenshot Directory**: Automatically created at `screenshots/e2e/`

## Test Coverage

The E2E tests cover:

✅ **Login System**

- Email/password authentication
- Form validation (empty fields, invalid credentials)
- Redirect to dashboard after login
- "Forgot password" link functionality
- Signup link navigation
- Remember me functionality
- Enter key form submission

✅ **Dashboard**

- Dashboard requires authentication
- Status cards (Account Status, Profile Completion, Security Score, Last Login)
- User-specific data display
- Security & Privacy section
- MFA warning badges
- Quick actions visibility
- Recent activity display
- Responsive layouts across all viewports

✅ **Password Reset**

- Forgot password page
- Email sending and confirmation
- Complete password reset flow
- Password reset with valid token
- Validation (empty fields, mismatched passwords, weak passwords)
- Security (old password invalidation)
- Invalid email handling
- Expired token errors

✅ **Navigation**

- Sidebar visibility and menu items
- Navigation to all account pages (Email, Password, MFA, Sessions)
- Mobile offcanvas menu
- Hamburger menu functionality
- Logout flow with confirmation
- Unauthorized access redirects
- Next parameter preservation
- Navigation state persistence

✅ **Signup/Registration**

- Signup form fields and layout
- Terms of Service checkbox
- Complete signup with email verification
- First-time dashboard access
- Form validation:
  - Empty required fields
  - Mismatched passwords
  - Weak passwords
  - Invalid email format
  - Duplicate email addresses
- Email verification workflow
- Mobile responsive forms

## Screenshots

Screenshots are automatically captured at key points during tests:

- Page layouts (desktop, tablet, mobile)
- Form states (empty, filled, error)
- Success/error messages
- Navigation states
- User flows

Screenshots are saved to: `screenshots/e2e/`

## Multi-Device Testing

All major flows are tested across three viewport sizes:

- **Desktop**: 1920x1080
- **Tablet**: 768x1024
- **Mobile**: 375x667

This ensures responsive design works correctly across all devices.

## Email Testing

Email functionality (verification, password reset) uses Django's `locmem` email backend (configured in test settings). Emails are captured in `mail.outbox` and parsed programmatically to extract verification/reset URLs.

## Best Practices

1. **Test Isolation**: Each test is independent and uses database transactions
2. **Page Object Pattern**: Helper functions abstract common actions
3. **Explicit Waits**: Tests use `wait_for_url()` and `wait_for_timeout()` for stability
4. **Screenshots**: Visual confirmation of page states
5. **Multi-Viewport**: Responsive design validation
6. **Accessibility**: Tests verify entrance/standard layouts consistently

## Troubleshooting

### Tests Failing Due to Timeouts

Increase timeout values in tests or run with `--slowmo`:

```powershell
poetry run pytest tests/e2e/ --slowmo 500
```

### Browser Not Found

Re-run Playwright installation:

```powershell
poetry run playwright install
```

### Screenshots Not Saving

Check that the `screenshots/e2e/` directory exists and is writable.

### Database Issues

Ensure tests use `@pytest.mark.django_db(transaction=True)` for proper database handling.

## Future Enhancements

Potential additions to the E2E test suite:

- Social login flows (OAuth)
- MFA/2FA setup and verification
- Email management (add/remove emails)
- Session management (multiple devices)
- Account deletion flow
- Accessibility testing (`page.accessibility.snapshot()`)
- Visual regression testing
- Performance metrics
- Browser compatibility (Firefox, WebKit)

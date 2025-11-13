SOCIALACCOUNT_ONLY = False
SOCIALACCOUNT_PROVIDERS = {
    "orcid": {
        "BASE_DOMAIN": "sandbox.orcid.org",  # for the sandbox API
    },
    "github": {"VERIFIED_EMAIL": True},
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "apple": {
        "APPS": [
            {
                # Your service identifier.
                "client_id": "your.service.id",
                # The Key ID (visible in the "View Key Details" page).
                "secret": "KEYID",
                # Member ID/App ID Prefix -- you can find it below your name
                # at the top right corner of the page, or it’s your App ID
                # Prefix in your App ID.
                "key": "MEMAPPIDPREFIX",
                "settings": {
                    # The certificate you downloaded when generating the key.
                    "certificate_key": """-----BEGIN PRIVATE KEY-----
s3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr
3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3
c3ts3cr3t
-----END PRIVATE KEY-----
"""
                },
            }
        ]
    },
}

if not SOCIALACCOUNT_ONLY:
    ACCOUNT_LOGIN_BY_CODE_ENABLED = True


MFA_PASSKEY_LOGIN_ENABLED = True
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FIELDS = ("first_name", "last_name", "password1*", "password2*", "email*")

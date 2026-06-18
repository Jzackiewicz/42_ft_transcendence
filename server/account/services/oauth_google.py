import base64
import hashlib
import secrets

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from account.models import SocialAccount

User = get_user_model()

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
OAUTH_SCOPES = "openid email profile"


OAUTH_STATE_COOKIE = "oauth_google_state"
OAUTH_STATE_MAX_AGE_SECONDS = 600
OAUTH_COOKIE_PATH = "/api/account/oauth/google/"


class OAuthErrorCode:
    CANCELLED = "cancelled"
    MISSING_PARAMS = "missing_params" # missing code/state/cookie on callback
    INVALID_STATE = "invalid_state" # cookie signature or expiry failed
    STATE_MISMATCH = "state_mismatch" # cookie state != query state (CSRF guard)
    EMAIL_NOT_VERIFIED = "email_not_verified"
    EXCHANGE_FAILED = "exchange_failed"
    SERVER_ERROR = "server_error" # any other unexpected error


def _b64url(raw: bytes) -> str:
    """URL-safe base64 with padding stripped (PKCE requires this exact format)"""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def build_authorize_url() -> tuple[str, str, str]:
    # returns (authorize_url, state, code_verifier).

    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = _b64url(hashlib.sha256(code_verifier.encode("ascii")).digest())

    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": OAUTH_SCOPES,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "online",
        "prompt": "select_account",
    }
    encoded = "&".join(
        f"{k}={requests.utils.quote(v, safe='')}" for k, v in params.items()
    )
    return f"{GOOGLE_AUTHORIZE_URL}?{encoded}", state, code_verifier


def exchange_code_for_id_token(code: str, code_verifier: str) -> dict:
    # trade the authorization code for tokens then verify the id token

    resp = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "code": code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        },
        timeout=10,
    )
    if resp.status_code != 200:
        raise ValidationError(OAuthErrorCode.EXCHANGE_FAILED)

    payload = resp.json()
    id_token_jwt = payload.get("id_token")
    if not id_token_jwt:
        raise ValidationError(OAuthErrorCode.EXCHANGE_FAILED)

    try:
        claims = id_token.verify_oauth2_token(
            id_token_jwt,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except ValueError:
        raise ValidationError(OAuthErrorCode.EXCHANGE_FAILED)

    if not claims.get("email_verified"):
        raise ValidationError(OAuthErrorCode.EMAIL_NOT_VERIFIED)

    return claims


@transaction.atomic
def get_link_or_create_user(claims: dict) -> User:
    sub = claims["sub"]
    email = claims["email"]
    name = claims.get("name") or email.split("@")[0]

    # case 1: returning user
    existing_link = (
        SocialAccount.objects
        .filter(provider=SocialAccount.PROVIDER_GOOGLE, uid=sub)
        .select_related("user")
        .first()
    )
    if existing_link:
        return existing_link.user

    # case 2: link to existing local account by email
    user = User.objects.filter(email=email).first()
    if user:
        SocialAccount.objects.create(
            user=user,
            provider=SocialAccount.PROVIDER_GOOGLE,
            uid=sub,
        )
        return user

    # case 3: create new account
    base_username = "".join(c for c in name if c.isalnum())[:140] or f"google_{sub[:8]}"
    username = base_username
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base_username}{suffix}"

    user = User.objects.create_user(username=username, email=email)
    user.set_unusable_password()
    user.save()

    SocialAccount.objects.create(
        user=user,
        provider=SocialAccount.PROVIDER_GOOGLE,
        uid=sub,
    )
    return user

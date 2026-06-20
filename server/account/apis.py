"""
This module contains API endpoints (controllers/views).
Each view is responsible only for:
  - Parsing and validating the incoming request
  - Delegating to the appropriate selector (reads) or service (writes)
  - Returning a serialized response

No business logic or direct ORM access belongs here.
"""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate, login, logout
from .permissions import IsSelfOrReadOnly, IsAnonymous
from django.contrib.auth import login as django_login
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .presence import PresenceRegistry

from .selectors import (
    user_get_by_id,
    user_list,
    profile_get_by_user_id,
    profile_list,
)
from .serializers import (
    UserRegisterInputSerializer,
    UserOutputSerializer,
    UserUpdateInputSerializer,
    UserProfileOutputSerializer,
    UserProfileAvatarInputSerializer,
    UserLoginInputSerializer,
    UserReauthSerializer,
)
from .services.profiles import (
    user_create,
    user_update_basic_info,
    user_soft_delete,
    profile_update_avatar,
    profile_clear_avatar,
)
from .services.oauth_google import (
    build_authorize_url,
    exchange_code_for_id_token,
    get_link_or_create_user,
    OAuthErrorCode,
    OAUTH_STATE_COOKIE,
    OAUTH_STATE_MAX_AGE_SECONDS,
    OAUTH_COOKIE_PATH,
)


def _oauth_error_redirect(code: str) -> HttpResponseRedirect:
    """All OAuth failure paths funnel through here so the SPA sees a
    consistent shape: /login?oauth_error=<stable_code>. Never echo Google's
    raw error string or an exception message — they're noisy and can hint
    at server config."""
    return HttpResponseRedirect(f"/login?oauth_error={code}")

# ---------------------------------------------------------------------------
# User endpoints
# ---------------------------------------------------------------------------


class UserListApi(APIView):
    @extend_schema(
        request=None,
        responses={200: UserOutputSerializer(many=True)},
        description="List all users.",
    )
    def get(self, request):
        users = user_list()
        output_serializer = UserOutputSerializer(users, many=True, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserDetailApi(APIView):
    permission_classes = [IsSelfOrReadOnly]

    @extend_schema(
        request=None,
        responses={200: UserOutputSerializer},
        description="Retrieve a user by ID.",
    )
    def get(self, request, user_id: int):
        user = user_get_by_id(user_id=user_id)
        output_serializer = UserOutputSerializer(user, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# UserProfile endpoints
# ---------------------------------------------------------------------------


@method_decorator(ensure_csrf_cookie, name="dispatch")
class UserProfileMeApi(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        request=None,
        responses={
            200: UserProfileOutputSerializer,
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        description="Retrieve the authenticated user's profile information.",
    )
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        profile = profile_get_by_user_id(user_id=request.user.id)
        output_serializer = UserProfileOutputSerializer(profile, context={"request": request})
        return Response(output_serializer.data)

    @extend_schema(
        request=UserUpdateInputSerializer,
        responses={
            200: UserProfileOutputSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        description="Update username or email for the authenticated user.",
    )
    def patch(self, request):
        input_serializer = UserUpdateInputSerializer(
            data=request.data, context={"request": request}
        )
        input_serializer.is_valid(raise_exception=True)

        try:
            user = user_update_basic_info(
                user=request.user, **input_serializer.validated_data
            )
        except ValidationError as e:
            return Response(
                {"detail": list(e.messages)[0]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = UserProfileOutputSerializer(user.profile, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserReauthSerializer,
        responses={
            204: None,
            400: {
                "type": "object",
                "additionalProperties": True,
                "description": "Missing or invalid password payload.",
            },
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        description="Soft-delete own account. Requires password confirmation.",
    )
    def delete(self, request):
        input_serializer = UserReauthSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=request.user.username,
            password=input_serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_soft_delete(user=request.user)
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileListApi(APIView):
    @extend_schema(
        request=None,
        responses={200: UserProfileOutputSerializer(many=True)},
        description="List all user profiles.",
    )
    def get(self, request):
        profiles = profile_list()
        output_serializer = UserProfileOutputSerializer(profiles, many=True, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserProfileDetailApi(APIView):
    @extend_schema(
        request=None,
        responses={200: UserProfileOutputSerializer},
        description="Retrieve the profile for a given user ID.",
    )
    def get(self, request, user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)
        output_serializer = UserProfileOutputSerializer(profile, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserProfileAvatarApi(APIView):
    permission_classes = [IsSelfOrReadOnly]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'avatar': {'type': 'string', 'format': 'binary'},
                },
            }
        },
        responses={200: UserProfileOutputSerializer},
        description="Upload or replace the avatar for a user profile.",
    )
    def post(self, request, user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)

        input_serializer = UserProfileAvatarInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        profile = profile_update_avatar(
            profile=profile, **input_serializer.validated_data
        )

        output_serializer = UserProfileOutputSerializer(profile, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses={204: None},
        description="Remove the avatar from a user profile.",
    )
    def delete(self, request, user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)
        profile_clear_avatar(profile=profile)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# User Register/Login/Logout endpoints
# ---------------------------------------------------------------------------


class UserRegisterApi(APIView):
    permission_classes = [IsAnonymous]

    @extend_schema(
        request=UserRegisterInputSerializer,
        responses={
            201: UserOutputSerializer,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        description="Register a new user account.",
    )
    def post(self, request):
        input_serializer = UserRegisterInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = user_create(**input_serializer.validated_data)

        output_serializer = UserOutputSerializer(user, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class UserLoginApi(APIView):
    permission_classes = [IsAnonymous]

    @extend_schema(
        request=UserLoginInputSerializer,
        responses={
            200: UserOutputSerializer,
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        description="Login",
    )
    def post(self, request):
        # validate input
        input_serializer = UserLoginInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=input_serializer.validated_data["identifier"],
            password=input_serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response(UserOutputSerializer(user, context={"request": request}).data, status=status.HTTP_200_OK)

class UserLogoutApi(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            204: None,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        description="Log the current user out and clear the session.",
    )
    def post(self, request):
        user_id = request.user.id
        logout(request)
        PresenceRegistry.clear_user(user_id)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "presence",
            {"type": "presence.update", "user_id": user_id, "is_online": False},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class GoogleOAuthLoginApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        authorize_url, state, code_verifier = build_authorize_url()

        signer = TimestampSigner()
        signed = signer.sign(f"{state}:{code_verifier}")

        response = HttpResponseRedirect(authorize_url)
        response.set_cookie(
            OAUTH_STATE_COOKIE,
            signed,
            max_age=OAUTH_STATE_MAX_AGE_SECONDS,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path=OAUTH_COOKIE_PATH,
        )
        return response


class GoogleOAuthCallbackApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        google_error = request.GET.get("error")
        if google_error:
            code = (
                OAuthErrorCode.CANCELLED
                if google_error == "access_denied"
                else OAuthErrorCode.SERVER_ERROR
            )
            return _oauth_error_redirect(code)

        signed = request.COOKIES.get(OAUTH_STATE_COOKIE)
        state = request.GET.get("state")
        code = request.GET.get("code")

        if not signed or not state or not code:
            return _oauth_error_redirect(OAuthErrorCode.MISSING_PARAMS)

        signer = TimestampSigner()
        try:
            unsigned = signer.unsign(signed, max_age=OAUTH_STATE_MAX_AGE_SECONDS)
        except (BadSignature, SignatureExpired):
            return _oauth_error_redirect(OAuthErrorCode.INVALID_STATE)

        # CSRF check: state in cookie must equal state Google echoed back.
        expected_state, code_verifier = unsigned.split(":", 1)
        if state != expected_state:
            return _oauth_error_redirect(OAuthErrorCode.STATE_MISMATCH)

        try:
            claims = exchange_code_for_id_token(code, code_verifier)
            user = get_link_or_create_user(claims)
        except ValidationError as e:
            return _oauth_error_redirect(list(e.messages)[0])
        except Exception:
            return _oauth_error_redirect(OAuthErrorCode.SERVER_ERROR)

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        response = HttpResponseRedirect("/home")
        # clean up used state cookie so it can't be replayed
        response.delete_cookie(OAUTH_STATE_COOKIE, path=OAUTH_COOKIE_PATH)
        return response

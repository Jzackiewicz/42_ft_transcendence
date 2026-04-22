"""
This module contains API endpoints (controllers/views).
Each view is responsible only for:
  - Parsing and validating the incoming request
  - Delegating to the appropriate selector (reads) or service (writes)
  - Returning a serialized response

No business logic or direct ORM access belongs here.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate, login, logout

from .selectors import (
    user_get_by_id,
    user_list,
    profile_get_by_user_id,
    profile_list,
    profile_list_friends,
)
from .serializers import (
    UserRegisterInputSerializer,
    UserOutputSerializer,
    UserUpdateInputSerializer,
    UserProfileOutputSerializer,
    UserProfileAvatarInputSerializer,
    UserProfileFriendOutputSerializer,
    UserLoginInputSerializer
)
from .services import (
    user_create,
    user_update_basic_info,
    profile_update_avatar,
    profile_clear_avatar,
    profile_add_friend,
    profile_remove_friend,
)

# ---------------------------------------------------------------------------
# User endpoints
# ---------------------------------------------------------------------------

class UserRegisterApi(APIView):

    permission_classes = []

    @extend_schema(
        request=UserRegisterInputSerializer,
        responses={201: UserOutputSerializer},
        description="Register a new user account.",
    )
    def post(self, request):
        input_serializer = UserRegisterInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = user_create(**input_serializer.validated_data)

        output_serializer = UserOutputSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class UserListApi(APIView):

    @extend_schema(
        responses={200: UserOutputSerializer(many=True)},
        description="List all users.",
    )
    def get(self, request):
        users = user_list()
        output_serializer = UserOutputSerializer(users, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserDetailApi(APIView):

    @extend_schema(
        responses={200: UserOutputSerializer},
        description="Retrieve a user by ID.",
    )
    def get(self, request, user_id: int):
        user = user_get_by_id(user_id=user_id)
        output_serializer = UserOutputSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserUpdateInputSerializer,
        responses={200: UserOutputSerializer},
        description="Update username or email for a user.",
    )
    def patch(self, request, user_id: int):
        user = user_get_by_id(user_id=user_id)

        input_serializer = UserUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = user_update_basic_info(user=user, **input_serializer.validated_data)

        output_serializer = UserOutputSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# UserProfile endpoints
# ---------------------------------------------------------------------------

class UserProfileListApi(APIView):

    @extend_schema(
        responses={200: UserProfileOutputSerializer(many=True)},
        description="List all user profiles.",
    )
    def get(self, request):
        profiles = profile_list()
        output_serializer = UserProfileOutputSerializer(profiles, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserProfileDetailApi(APIView):

    @extend_schema(
        responses={200: UserProfileOutputSerializer},
        description="Retrieve the profile for a given user ID.",
    )
    def get(self, request, user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)
        output_serializer = UserProfileOutputSerializer(profile)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserProfileAvatarApi(APIView):

    @extend_schema(
        request=UserProfileAvatarInputSerializer,
        responses={200: UserProfileOutputSerializer},
        description="Upload or replace the avatar for a user profile.",
    )
    def post(self, request, user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)

        input_serializer = UserProfileAvatarInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        profile = profile_update_avatar(profile=profile, **input_serializer.validated_data)

        output_serializer = UserProfileOutputSerializer(profile)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={204: None},
        description="Remove the avatar from a user profile.",
    )
    def delete(self, request, user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)
        profile_clear_avatar(profile=profile)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileFriendListApi(APIView):

    @extend_schema(
        responses={200: UserProfileFriendOutputSerializer(many=True)},
        description="List friends of a user profile.",
    )
    def get(self, request, user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)
        friends = profile_list_friends(profile=profile)
        output_serializer = UserProfileFriendOutputSerializer(friends, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserProfileFriendDetailApi(APIView):

    @extend_schema(
        request=None,
        responses={204: None},
        description="Add a user as a friend.",
    )
    def post(self, request, user_id: int, friend_user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)
        friend_profile = profile_get_by_user_id(user_id=friend_user_id)
        profile_add_friend(profile=profile, friend_profile=friend_profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=None,
        responses={204: None},
        description="Remove a user from friends.",
    )
    def delete(self, request, user_id: int, friend_user_id: int):
        profile = profile_get_by_user_id(user_id=user_id)
        friend_profile = profile_get_by_user_id(user_id=friend_user_id)
        profile_remove_friend(profile=profile, friend_profile=friend_profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---------------------------------------------------------------------------
# User Login/Logout endpoints
# ---------------------------------------------------------------------------

class UserLoginApi(APIView):
    permission_classes = [] #user isnt authenticated yet, so its available for everyone

    @extend_schema(
        request=UserLoginInputSerializer,
        responses={200: UserOutputSerializer},
        description="Login",
    )
    def post(self, request):
        # validate incoming data
        input_serializer = UserLoginInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # verify credentials, return None if wrong
        user = authenticate(request, 
                            username=input_serializer.validated_data["username"], 
                            password=input_serializer.validated_data["password"])
        
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # mark user as logged in & remember for future requests
        login(request, user)

        return Response(UserOutputSerializer(user).data, status=status.HTTP_200_OK)


class UserLogoutApi(APIView):
    @extend_schema(
        request=None,
        responses={204: None},
        description="Log the current user out and clear the session.",
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

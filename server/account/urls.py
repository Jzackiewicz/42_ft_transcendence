from django.urls import path

from account import apis

urlpatterns = [
    # register/login/logout endpoints
    path("users/register/", apis.UserRegisterApi.as_view(), name="user-register"),
    path("users/login/", apis.UserLoginApi.as_view(), name="user-login"),
    path("users/logout/", apis.UserLogoutApi.as_view(), name="user-logout"),
    # User endpoints
    path("users/me/", apis.UserMeApi.as_view(), name="user-me"),
    path("users/", apis.UserListApi.as_view(), name="user-list"),
    path("users/<int:user_id>/", apis.UserDetailApi.as_view(), name="user-detail"),
    # UserProfile endpoints
    path("profiles/me/", apis.UserProfileMeApi.as_view(), name="profile-me"),
    path("profiles/", apis.UserProfileListApi.as_view(), name="profile-list"),
    path(
        "profiles/<int:user_id>/",
        apis.UserProfileDetailApi.as_view(),
        name="profile-detail",
    ),
    path(
        "profiles/<int:user_id>/avatar/",
        apis.UserProfileAvatarApi.as_view(),
        name="profile-avatar",
    ),
]

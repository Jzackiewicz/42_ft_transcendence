from django.urls import path

from account import apis

urlpatterns = [
    # login/logout endpoints
    path('users/login/', apis.UserLoginAPI.as_view(), name='user-login'),
    path('users/logout/', apis.UserLogoutAPI.as_view(), name='user-logout'),
    # User endpoints
    path('users/register/', apis.UserRegisterApi.as_view(), name='user-register'),
    path('users/', apis.UserListApi.as_view(), name='user-list'),
    path('users/<int:user_id>/', apis.UserDetailApi.as_view(), name='user-detail'),
    # UserProfile endpoints
    path('profiles/', apis.UserProfileListApi.as_view(), name='profile-list'),
    path('profiles/<int:user_id>/', apis.UserProfileDetailApi.as_view(), name='profile-detail'),
    path('profiles/<int:user_id>/avatar/', apis.UserProfileAvatarApi.as_view(), name='profile-avatar'),
    path('profiles/<int:user_id>/friends/', apis.UserProfileFriendListApi.as_view(), name='profile-friend-list'),
    path(
        'profiles/<int:user_id>/friends/<int:friend_user_id>/',
        apis.UserProfileFriendDetailApi.as_view(),
        name='profile-friend-detail',
    ),
]

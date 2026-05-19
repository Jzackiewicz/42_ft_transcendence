from rest_framework import permissions


class IsSelfOrReadOnly(permissions.BasePermission):
    message = "You don't have permissions to modify this user's data."
    user_kwarg = "user_id"

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        url_user_id = view.kwargs.get(self.user_kwarg)
        if url_user_id is None:
            return False

        return request.user.id == url_user_id


class IsAnonymous(permissions.BasePermission):
    """
    Allows access only to unauthenticated users.
    """

    def has_permission(self, request, view):
        return not request.user or not request.user.is_authenticated

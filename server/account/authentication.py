from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class ActionSessionAuthentication(SessionAuthentication):
    """
    Custom SessionAuthentication that returns 401 instead of 403
    for unauthenticated requests.
    """
    def authenticate_header(self, request):
        return 'Session'


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username
        if identifier is None or password is None:
            return None
        try:
            user = User.objects.get(
                Q(email__iexact=identifier) | Q(username__iexact=identifier)
            )
        except User.DoesNotExist:
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
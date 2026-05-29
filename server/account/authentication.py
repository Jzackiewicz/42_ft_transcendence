from rest_framework.authentication import SessionAuthentication

class ActionSessionAuthentication(SessionAuthentication):
    """
    Custom SessionAuthentication that returns 401 instead of 403
    for unauthenticated requests.
    """
    def authenticate_header(self, request):
        return 'Session'

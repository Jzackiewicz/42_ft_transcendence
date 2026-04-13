from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'

    def ready(self) -> None:
        # Connect signal handlers
        import account.signals 

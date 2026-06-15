from django.core.management.base import BaseCommand
from game.models import GameSession

class Command(BaseCommand):
    help = "Cleans up stuck active game sessions on server boot."

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up stuck active game sessions...")
        try:
            updated = GameSession.objects.exclude(
                current_status=GameSession.Status.GAME_OVER
            ).update(
                current_status=GameSession.Status.GAME_OVER,
                end_reason=GameSession.EndReason.CANCELLED
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully cleaned up {updated} sessions."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to clean up sessions: {e}"))

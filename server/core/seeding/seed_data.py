import os
import sys
import uuid
import django
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

# Bootstrap Django
# Ensure server directory is in python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction
from social.models import Friendship
from game.models import (
    GameSession,
    SessionPlayer,
    Question,
    SessionQuestion,
    AnswerAttempt,
)

User = get_user_model()


def load_source_avatar(source_filename, target_filename):
    img_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "img", source_filename
    )
    src_ext = os.path.splitext(source_filename)[1].lower()
    tgt_ext = os.path.splitext(target_filename)[1].lower()
    
    if src_ext != tgt_ext:
        with Image.open(img_path) as img:
            buf = BytesIO()
            if tgt_ext == ".png":
                fmt = "PNG"
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
            elif tgt_ext in (".jpg", ".jpeg"):
                fmt = "JPEG"
                if img.mode != "RGB":
                    img = img.convert("RGB")
            else:
                fmt = "WEBP"
            img.save(buf, format=fmt)
            return ContentFile(buf.getvalue(), name=target_filename)
    else:
        with open(img_path, "rb") as f:
            return ContentFile(f.read(), name=target_filename)


def main():
    print("Loading questions fixture...")
    try:
        # Load questions.json from same directory as this script
        questions_json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "questions.json"
        )
        call_command("loaddata", questions_json_path)
        print("Questions fixture loaded.")
    except Exception as e:
        print(f"Questions fixture load failed: {e}")

    with transaction.atomic():
        # 1. Create mock users
        usernames = ["alice", "bob", "carol", "dave", "eve", "frank", "grace", "heidi", "rick"]
        avatar_mapping = {
            "alice": ("Meme_Man_on_transparent_background.webp", "avatar_alice.webp"),
            "bob": ("doge.jpg", "avatar_bob.jpg"),
            "carol": ("gru.jpg", "avatar_carol.jpg"),
            "frank": ("peppocool.jpg", "avatar_frank.jpg"),
            "grace": ("wazowsky.png", "avatar_grace.png"),
            "rick": ("rick.webp", "rick.png"),
        }
        users = {}
        for name in usernames:
            user, created = User.objects.get_or_create(
                username=name,
                defaults={"email": f"{name}@example.com"},
            )
            if created:
                user.set_password("password123")
                user.save()
                print(f"Created user: {name}")
            else:
                print(f"User already exists: {name}")

            # Check and save avatar if specified
            profile = user.profile
            if name in avatar_mapping:
                source_fn, target_fn = avatar_mapping[name]
                if profile.avatar:
                    try:
                        profile.avatar.delete(save=False)
                    except Exception as e:
                        print(f"Failed to delete old avatar for {name}: {e}")
                
                try:
                    avatar_file = load_source_avatar(source_fn, target_fn)
                    profile.avatar.save(target_fn, avatar_file, save=False)
                    profile.save()
                    print(f"Assigned avatar to {name}")
                except Exception as e:
                    print(f"Failed to assign avatar to {name}: {e}")

            users[name] = user

        # 2. Create friendships (bidirectional)
        friendship_pairs = [
            ("alice", "bob"),
            ("alice", "carol"),
            ("alice", "dave"),
            ("bob", "carol"),
            ("carol", "dave"),
            ("frank", "grace"),
            ("grace", "heidi"),
            ("heidi", "alice"),
            ("frank", "bob"),
        ]
        for u1_name, u2_name in friendship_pairs:
            u1 = users[u1_name]
            u2 = users[u2_name]

            f1, c1 = Friendship.objects.get_or_create(user=u1, friend=u2)
            f2, c2 = Friendship.objects.get_or_create(user=u2, friend=u1)
            if c1 or c2:
                print(f"Established friendship: {u1_name} <-> {u2_name}")

        # 3. Create mock completed game sessions
        game_configs = [
            {
                "uuid": "00000000-0000-0000-0000-000000000001",
                "players": ["alice", "bob", "carol"],
                "winner": "alice",
                "points": {"alice": 80, "bob": 40, "carol": 10},
                "lives": {"alice": 3, "bob": 0, "carol": 0},
            },
            {
                "uuid": "00000000-0000-0000-0000-000000000002",
                "players": ["bob", "carol", "dave"],
                "winner": "carol",
                "points": {"bob": 20, "carol": 90, "dave": 50},
                "lives": {"bob": 0, "carol": 2, "dave": 0},
            },
            {
                "uuid": "00000000-0000-0000-0000-000000000003",
                "players": ["carol", "dave", "eve"],
                "winner": "dave",
                "points": {"carol": 30, "dave": 75, "eve": 40},
                "lives": {"carol": 0, "dave": 1, "eve": 0},
            },
            {
                "uuid": "00000000-0000-0000-0000-000000000004",
                "players": ["frank", "grace", "heidi"],
                "winner": "heidi",
                "points": {"frank": 15, "grace": 25, "heidi": 85},
                "lives": {"frank": 0, "grace": 0, "heidi": 3},
            },
        ]

        questions = list(Question.objects.all()[:5])
        if not questions:
            print("No Questions found. Cannot seed game sessions.")
            return

        for config in game_configs:
            session_uuid = uuid.UUID(config["uuid"])
            session, created = GameSession.objects.get_or_create(
                session_uuid=session_uuid,
                defaults={
                    "current_status": GameSession.Status.GAME_OVER,
                    "end_reason": GameSession.EndReason.LAST_PLAYER_ALIVE,
                    "question_asked_count": len(questions),
                },
            )
            if created:
                print(f"Seeding game session: {session_uuid}")

                # Create SessionPlayer records
                player_objs = {}
                for seat_idx, p_name in enumerate(config["players"]):
                    user_obj = users[p_name]
                    player_obj = SessionPlayer.objects.create(
                        session=session,
                        user=user_obj,
                        display_name=user_obj.username,
                        seat_number=seat_idx,
                        lives=config["lives"][p_name],
                        points=config["points"][p_name],
                        player_type=SessionPlayer.PlayerType.HUMAN,
                    )
                    player_objs[p_name] = player_obj

                # Set host and winner
                session.host_player = player_objs[config["players"][0]]
                session.winner = player_objs[config["winner"]]
                session.save()

                # Create SessionQuestion records
                session_questions = []
                for idx, q in enumerate(questions):
                    sq = SessionQuestion.objects.create(
                        session=session,
                        question=q,
                        order_index=idx,
                    )
                    session_questions.append(sq)

                # Create AnswerAttempt records for statistics
                for sq_idx, sq in enumerate(session_questions):
                    for p_name in config["players"]:
                        player = player_objs[p_name]
                        is_correct = (p_name == config["winner"]) or (sq_idx % 2 == 0)
                        AnswerAttempt.objects.create(
                            session=session,
                            player=player,
                            session_question=sq,
                            is_correct=is_correct,
                            is_timeout=False,
                            evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
                            answer_time_ms=1000 + (player.id * 150) % 1500,
                        )
            else:
                print(f"Game session already exists: {session_uuid}")

    print("Database seeding completed successfully.")


if __name__ == "__main__":
    main()

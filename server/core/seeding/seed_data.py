import os
import sys
import uuid
import django
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from account.models import SocialAccount
from social.models import Friendship, ChatMessage
from game.models import (
    GameSession,
    SessionPlayer,
    Question,
    SessionQuestion,
    AnswerAttempt,
)

User = get_user_model()

DM_ROOM_PREFIX = "dm_"

USER_CONFIGS = [
    {
        "username": "alice",
        "password": "Wonderland42!",
        "email": "alice@example.com",
        "avatar": ("Meme_Man_on_transparent_background.webp", "avatar_alice.webp"),
        "google_uid": "google_sub_alice_001",
    },
    {
        "username": "bob",
        "password": "Builder99@",
        "email": "bob@example.com",
        "avatar": ("doge.jpg", "avatar_bob.jpg"),
    },
    {
        "username": "carol",
        "password": "Danvers88#",
        "email": "carol@example.com",
        "avatar": ("gru.jpg", "avatar_carol.jpg"),
        "google_uid": "google_sub_carol_002",
    },
    {
        "username": "dave",
        "password": "Grohl77$",
        "email": "dave@example.com",
    },
    {
        "username": "eve",
        "password": "Online55%",
        "email": "eve@example.com",
    },
    {
        "username": "frank",
        "password": "Zappa66^",
        "email": "frank@example.com",
        "avatar": ("peppocool.jpg", "avatar_frank.jpg"),
        "google_uid": "google_sub_frank_003",
    },
    {
        "username": "grace",
        "password": "Hopper11!",
        "email": "grace@example.com",
        "avatar": ("wazowsky.png", "avatar_grace.png"),
    },
    {
        "username": "heidi",
        "password": "Klum22@",
        "email": "heidi@example.com",
    },
    {
        "username": "rick",
        "password": "Astley33#",
        "email": "rick@example.com",
        "avatar": ("rick.webp", "rick.png"),
    },
    {
        "username": "chad",
        "password": "Gigachad00!",
        "email": "chad@example.com",
        "avatar": ("chad.gif", "avatar_chad.gif"),
    },
]


def dm_room_name(user_a, user_b):
    lo, hi = sorted([user_a.id, user_b.id])
    return f"{DM_ROOM_PREFIX}{lo}_{hi}"


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


def seed_chat(user_a, user_b, messages):
    room = dm_room_name(user_a, user_b)
    if ChatMessage.objects.filter(room_name=room).exists():
        print(f"  Chat {room} already seeded, skipping")
        return
    for sender, text in messages:
        ChatMessage.objects.create(
            room_name=room,
            sender_username=sender.username,
            message=text,
        )
    print(f"  Seeded {len(messages)} messages in {room}")


def build_alice_bob_chat(alice, bob):
    a, b = alice, bob
    return [
        (a, "yo bob, wanna play tonight?"),
        (b, "sure, what time?"),
        (a, "around 9pm?"),
        (b, "perfect"),
        (a, "I have been practicing all week"),
        (b, "bold of you to assume that will help"),
        (a, "lmao you wish"),
        (b, "last game I had 90 points"),
        (a, "that was lucky"),
        (b, "or skill 🤔"),
        (a, "definitely luck"),
        (b, "ok ok we will see tonight"),
        (a, "bringing dave this time?"),
        (b, "nah he is busy"),
        (a, "what about carol?"),
        (b, "she said maybe"),
        (a, "ok I will message her"),
        (b, "cool"),
        (a, "do you want to use the same settings as last time?"),
        (b, "yeah 5 questions, 3 lives"),
        (a, "sounds good"),
        (b, "also can we add the timer? makes it more intense"),
        (a, "absolutely"),
        (b, "I have been thinking about the geography questions"),
        (a, "those are brutal"),
        (b, "I got one completely wrong last time"),
        (a, "which one?"),
        (b, "something about capitals in Africa"),
        (a, "haha I nailed that one"),
        (b, "ok now I really need to beat you tonight"),
        (a, "bring it"),
        (b, "also have you seen the new leaderboard?"),
        (a, "yes! I am third"),
        (b, "I am seventh, not impressed with myself"),
        (a, "top ten is still good"),
        (b, "eh"),
        (a, "grace is second place somehow"),
        (b, "she is really good at trivia"),
        (a, "I know, scary"),
        (b, "ok I need to study before tonight"),
        (a, "study? it is a trivia game not an exam"),
        (b, "same thing"),
        (a, "you are so weird"),
        (b, "and yet here you are playing with me"),
        (a, "fair point"),
        (b, "ok see you at 9"),
        (a, "wait can we do 9:30 instead?"),
        (b, "yeah fine"),
        (a, "thanks, I have dinner running late"),
        (b, "no worries"),
        (a, "also can you tell me if carol confirms?"),
        (b, "sure"),
        (a, "cool"),
        (b, "she just said yes btw"),
        (a, "nice! 3 player game"),
        (b, "just like old times"),
        (a, "remember when carol won 3 games in a row?"),
        (b, "do not remind me"),
        (a, "90 points she said"),
        (b, "ok I get it"),
        (a, "😂"),
        (b, "see you tonight, I will be ready"),
        (a, "we will see about that"),
    ]


def build_alice_carol_chat(alice, carol):
    a, c = alice, carol
    return [
        (c, "alice! did you see the new question pack?"),
        (a, "not yet, what is it about?"),
        (c, "science and technology!"),
        (a, "oh nice that is my weak spot"),
        (c, "same honestly"),
        (a, "we should practice together sometime"),
        (c, "yes! I was thinking that"),
        (a, "bob told me you are joining tonight"),
        (c, "yeah 9:30 right?"),
        (a, "exactly"),
        (c, "ok I will be there"),
        (a, "do you know what your best category is?"),
        (c, "history for sure"),
        (a, "figures, you always get those"),
        (c, "I spent too much time studying history in school"),
        (a, "at least it is useful now"),
        (c, "haha exactly"),
        (a, "my best is pop culture"),
        (c, "that explains a lot"),
        (a, "what is that supposed to mean"),
        (c, "nothing nothing 😇"),
        (a, "rude"),
        (c, "ok ok you are great at pop culture"),
        (a, "thank you"),
        (c, "so the game tonight, any strategy?"),
        (a, "just answer fast and hope for the best"),
        (c, "solid plan"),
        (a, "I have been doing pretty well lately"),
        (c, "I saw you on the leaderboard!"),
        (a, "third place baby"),
        (c, "very nice"),
        (a, "where are you?"),
        (c, "like 12th I think"),
        (a, "not bad"),
        (c, "I feel like I am getting better"),
        (a, "you really are"),
        (c, "remember when I lost in the first round against dave?"),
        (a, "lmao yes"),
        (c, "so embarrassing"),
        (a, "you have come a long way"),
        (c, "thank you that means a lot"),
        (a, "ok see you tonight"),
        (c, "can not wait"),
        (a, "bring your A game"),
        (c, "always do"),
        (a, "we will see 😏"),
        (c, "I will beat both of you tonight"),
        (a, "bold claim"),
        (c, "watch me"),
        (a, "ok ok challenge accepted"),
        (c, "game on"),
        (a, "👊"),
        (c, "👊"),
        (a, "see you at 9:30!"),
        (c, "see you then!"),
    ]


def build_bob_carol_chat(bob, carol):
    b, c = bob, carol
    return [
        (b, "carol are you coming tonight?"),
        (c, "yes alice already told me"),
        (b, "good good"),
        (c, "you ready to lose?"),
        (b, "excuse me?"),
        (c, "you heard me"),
        (b, "I had 90 points last session"),
        (c, "and I had 90 in the one before that"),
        (b, "ok fair"),
        (c, "so yeah, ready to lose?"),
        (b, "not a chance"),
        (c, "we will see at 9:30"),
        (b, "yeah we will"),
        (c, "may the best player win"),
        (b, "agreed"),
        (c, "spoiler: it will be me"),
        (b, "not if I have anything to say about it"),
        (c, "😂 ok bob"),
        (b, "you know I always come back strong"),
        (c, "true you did win that one time"),
        (b, "THAT ONE TIME? I have won multiple"),
        (c, "sure sure"),
    ]


def build_frank_grace_chat(frank, grace):
    f, g = frank, grace
    return [
        (f, "grace you are second on the leaderboard??"),
        (g, "haha yes I have been practicing"),
        (f, "how"),
        (g, "I just read a lot"),
        (f, "that is not fair"),
        (g, "it is called preparation 😊"),
        (f, "I am going to study before our next game"),
        (g, "good luck with that"),
        (f, "you doubt me?"),
        (g, "a little"),
        (f, "watch me climb that leaderboard"),
        (g, "I will be watching from second place"),
        (f, "for now"),
        (g, "forever"),
        (f, "we will have a rematch this weekend?"),
        (g, "Saturday?"),
        (f, "works for me"),
        (g, "ok Saturday it is"),
        (f, "heidi coming too?"),
        (g, "I will ask her"),
    ]


def build_chad_alice_chat(chad, alice):
    c, a = chad, alice
    return [
        (c, "hey alice, chad here"),
        (a, "oh hi! we matched in a game earlier right?"),
        (c, "yeah you wrecked me lol"),
        (a, "sorry! I just got lucky with the questions"),
        (c, "you knew every single one"),
        (a, "pop culture is kind of my thing"),
        (c, "clearly 😅"),
        (a, "rematch sometime?"),
        (c, "definitely, I need redemption"),
        (a, "anytime, just invite me to a session"),
    ]


def main():
    with transaction.atomic():
        # 1. Create users
        print("=== Creating users ===")
        users = {}
        for cfg in USER_CONFIGS:
            name = cfg["username"]
            user, created = User.objects.get_or_create(
                username=name,
                defaults={"email": cfg["email"]},
            )
            if created:
                user.set_password(cfg["password"])
                user.save()
                print(f"  Created: {name}")
            else:
                print(f"  Exists:  {name}")

            if "avatar" in cfg:
                profile = user.profile
                if not profile.avatar:
                    source_fn, target_fn = cfg["avatar"]
                    try:
                        avatar_file = load_source_avatar(source_fn, target_fn)
                        profile.avatar.save(target_fn, avatar_file, save=True)
                        print("    → avatar assigned")
                    except Exception as e:
                        print(f"    → avatar failed: {e}")

            if "google_uid" in cfg:
                _, sa_created = SocialAccount.objects.get_or_create(
                    provider=SocialAccount.PROVIDER_GOOGLE,
                    uid=cfg["google_uid"],
                    defaults={"user": user},
                )
                if sa_created:
                    print("    → Google account linked")

            users[name] = user

        # 2. Friendships
        print("\n=== Establishing friendships ===")
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
            ("chad", "alice"),
        ]
        for u1_name, u2_name in friendship_pairs:
            u1, u2 = users[u1_name], users[u2_name]
            f1, c1 = Friendship.objects.get_or_create(user=u1, friend=u2)
            f2, c2 = Friendship.objects.get_or_create(user=u2, friend=u1)
            if c1 or c2:
                print(f"  {u1_name} <-> {u2_name}")

        # 3. Game sessions
        print("\n=== Seeding game sessions ===")
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
            print("  No Questions found, skipping game sessions.")
        else:
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
                if not created:
                    print(f"  Session {session_uuid} already exists")
                    continue

                print(f"  Seeding session {session_uuid}")
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

                session.host_player = player_objs[config["players"][0]]
                session.winner = player_objs[config["winner"]]
                session.save()

                session_questions = []
                for idx, q in enumerate(questions):
                    sq = SessionQuestion.objects.create(
                        session=session,
                        question=q,
                        order_index=idx,
                    )
                    session_questions.append(sq)

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

        # 4. Chat messages
        print("\n=== Seeding chat messages ===")
        alice = users["alice"]
        bob = users["bob"]
        carol = users["carol"]
        frank = users["frank"]
        grace = users["grace"]
        chad = users["chad"]

        seed_chat(alice, bob, build_alice_bob_chat(alice, bob))  # 63 msgs
        seed_chat(alice, carol, build_alice_carol_chat(alice, carol))  # 56 msgs
        seed_chat(bob, carol, build_bob_carol_chat(bob, carol))  # 21 msgs
        seed_chat(frank, grace, build_frank_grace_chat(frank, grace))  # 19 msgs
        seed_chat(chad, alice, build_chad_alice_chat(chad, alice))  # 10 msgs

    # 5. Summary
    print("\n" + "=" * 60)
    print("  SEEDING SUMMARY")
    print("=" * 60)
    print(f"  {'USERNAME':<10}  {'PASSWORD':<16}  {'TYPE':<12}  AVATAR")
    print(f"  {'-' * 10}  {'-' * 16}  {'-' * 12}  {'-' * 20}")
    google_uids = {cfg["username"] for cfg in USER_CONFIGS if "google_uid" in cfg}
    for cfg in USER_CONFIGS:
        utype = "Google+Local" if cfg["username"] in google_uids else "Local"
        has_avatar = "avatar" in cfg
        avatar_str = cfg["avatar"][0] if has_avatar else "none"
        print(
            f"  {cfg['username']:<10}  {cfg['password']:<16}  {utype:<12}  {avatar_str}"
        )
    print("=" * 60)
    print("  All users email: <username>@example.com")
    print("  Google-linked:   alice, carol, frank (fake UIDs, dev only)")
    print("=" * 60)
    print("\nDatabase seeding completed successfully.")


if __name__ == "__main__":
    main()

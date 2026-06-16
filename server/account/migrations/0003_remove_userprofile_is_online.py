from django.db import migrations


class Migration(migrations.Migration):
    """
    Drop UserProfile.is_online.

    The field was never written to anywhere in the codebase; presence is
    tracked at runtime by `account.presence.PresenceRegistry` and surfaced
    in serializers via SerializerMethodField. Persisting it created a split
    source of truth (the /me endpoint always returned the stale False
    while /social/friends/ read from the registry) and would leave stale
    True rows on ungraceful shutdowns.
    """

    dependencies = [
        ('account', '0002_remove_userprofile_friends'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='is_online',
        ),
    ]

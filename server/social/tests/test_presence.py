from unittest import TestCase

from social.presence import PresenceRegistry


class PresenceRegistryTests(TestCase):
    def setUp(self):
        # Reset shared state between tests so they don't leak into each other.
        PresenceRegistry._connections.clear()

    def test_first_connect_is_transition(self):
        self.assertTrue(PresenceRegistry.mark_online(1, "a"))

    def test_second_tab_is_not_transition(self):
        PresenceRegistry.mark_online(1, "a")
        self.assertFalse(PresenceRegistry.mark_online(1, "b"))

    def test_last_disconnect_is_transition(self):
        PresenceRegistry.mark_online(1, "a")
        self.assertTrue(PresenceRegistry.mark_offline(1, "a"))

    def test_offline_when_other_tab_remains(self):
        PresenceRegistry.mark_online(1, "a")
        PresenceRegistry.mark_online(1, "b")
        self.assertFalse(PresenceRegistry.mark_offline(1, "a"))

    def test_mark_offline_unknown_user_is_no_op(self):
        self.assertFalse(PresenceRegistry.mark_offline(999, "a"))

    def test_clear_user_removes_all_sockets(self):
        PresenceRegistry.mark_online(1, "a")
        PresenceRegistry.mark_online(1, "b")
        PresenceRegistry.clear_user(1)
        self.assertFalse(PresenceRegistry.is_online(1))

    def test_online_user_ids_bulk(self):
        PresenceRegistry.mark_online(1, "a")
        PresenceRegistry.mark_online(3, "b")
        self.assertEqual(
            PresenceRegistry.online_user_ids([1, 2, 3]),
            {1, 3},
        )
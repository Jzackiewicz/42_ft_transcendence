from game.fsm import GameStateMachine
from django.test import SimpleTestCase


class GameStateMachineTest(SimpleTestCase):
	def test_initial_state_is_lobby(self):
		fsm = GameStateMachine()
		self.assertTrue(fsm.lobby.is_active)
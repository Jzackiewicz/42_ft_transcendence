from game.fsm import GameStateMachine
from django.test import SimpleTestCase
from game.fsm import GameStateMachine
from statemachine.contrib.diagram import quickchart_write_svg



class ShowFSMDiagram(SimpleTestCase):
	def test_show_fsm_diagram(self):
		sm = GameStateMachine(players_count=2)
		quickchart_write_svg(sm, "game_state_machine.svg")
from pathlib import Path
from django.test import SimpleTestCase

from game.fsm import GameStateMachine


class GameStateMachineDiagramTest(SimpleTestCase):
	def test_can_generate_fsm_diagram_png(self):
		sm = GameStateMachine()

		graph = sm._graph()  # pydot.Dot
		output_path = Path("tests/game_state_machine.png")
		output_path.parent.mkdir(parents=True, exist_ok=True)

		graph.write_png(str(output_path))

		self.assertTrue(output_path.exists())
		self.assertGreater(output_path.stat().st_size, 0)
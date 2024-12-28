import unittest
from app.components import Node
from app.agents import AgentState

class TestState(unittest.TestCase):

    def setUp(self):
        self.test_node = Node(4, 9)

    def test_state_creation(self):
        rot = 90
        state = AgentState(self.test_node, rot)
        self.assertEqual(state.node, self.test_node)
        self.assertEqual(state.rot, rot)

if __name__ == '__main__':
    unittest.main()

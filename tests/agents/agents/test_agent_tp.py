import unittest
from app.agents import Agent_TP, AgentState
from app.components import Node

class TestAgentTP(unittest.TestCase):

    def setUp(self):
        node = Node(4, 9)
        rot = 90
        self.starting_state = AgentState(node, rot)

    def test_spawn_at_correct_location(self):
        agent = Agent_TP(self.starting_state)
        self.assertEqual(agent.state, self.starting_state)

    def test_move_valid_timestamp(self):
        agent = Agent_TP(self.starting_state)
        agent.move(1)
        self.assertEqual(agent.state, self.starting_state)

    def test_move_invalid_timestamp(self):
        agent = Agent_TP(self.starting_state)
        next_timestamp = 2
        with self.assertRaises(NotImplementedError):
            agent.move(next_timestamp)

if __name__ == '__main__':
    unittest.main()
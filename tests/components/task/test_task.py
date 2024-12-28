import unittest
from app.components import Node, Task

class TestTask(unittest.TestCase):
    
    def setUp(self):
        self.node = Node(4, 9)

    def test_task_creation(self):
        task = Task(self.node, 16)
        self.assertEqual(task.node, self.node)
        self.assertEqual(task.add_time, 16)
        self.assertIsNone(task.pickup_time)
        self.assertIsNone(task.delivery_time)
        self.assertIsNone(task.assigned_agent)

    def test_task_pickup(self):
        task = Task(self.node, 16)
        task.pickup(25, 1)
        self.assertEqual(task.pickup_time, 25)
        self.assertEqual(task.assigned_agent, 1)
    
    def test_task_delivery(self):
        task = Task(self.node, 16)
        task.pickup(25, 1)
        task.deliver(49, 1)
        self.assertEqual(task.delivery_time, 49)

    def test_task_delivery_without_pickup(self):
        task = Task(self.node, 16)
        with self.assertRaises(ValueError) as context:
            task.deliver(49, 1)
        self.assertEqual(str(context.exception), f"Agent 1 is not the assigned agent for task {task.id}")
    
    def test_task_delivery_wrong_agent(self):
        task = Task(self.node, 16)
        task.pickup(25, 1)
        with self.assertRaises(ValueError) as context:
            task.deliver(49, 2)
        self.assertEqual(str(context.exception), f"Agent 2 is not the assigned agent for task {task.id}")


if __name__ == '__main__':
    unittest.main()

import unittest
from app.components import Node

class TestNode(unittest.TestCase):
    
    def test_node_creation(self):
        node = Node(10, 20)
        self.assertEqual(node.x_coord, 10)
        self.assertEqual(node.y_coord, 20)

    def test_node_equality_same_coordinates(self):
        node1 = Node(10, 20)
        node2 = Node(10, 20)
        self.assertEqual(node1, node2)

    def test_node_equality_different_coordinates(self):
        node1 = Node(10, 20)
        node2 = Node(30, 40)
        self.assertNotEqual(node1, node2)

    def test_node_equality_with_non_node(self):
        node = Node(10, 20)
        non_node = (10, 20)
        with self.assertRaises(TypeError) as context:
            node == non_node
        self.assertEqual(str(context.exception), "Cannot compare 'Node' with 'tuple'")

if __name__ == '__main__':
    unittest.main()

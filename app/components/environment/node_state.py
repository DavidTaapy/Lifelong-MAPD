from enum import Enum

from app.components.environment.node import Node

class NodeStatus(Enum):
    FREE = "FREE"
    OBSTACLE = "OBSTACLE"
    TASK_ENDPOINT = "TASK_ENDPOINT"
    NON_TASK_ENDPOINT = "NON_TASK_ENDPOINT"

class NodeState:

    def __init__(self, node: Node, node_status: NodeStatus):
        self.node = node
        self.node_status = node_status
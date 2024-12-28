from app.components.environment.node_state import NodeState, NodeStatus
from app.components.environment.node import Node

class Map:

    def __init__ (self):
        self.env: dict[(int, int), NodeState] = {}

    def get_node_state(self, x_coord: int, y_coord: int) -> NodeState:
        if (x_coord, y_coord) in self.env:
            return self.env[(x_coord, y_coord)]
        else:
            raise ValueError(f"Node at coordinates ({x_coord}, {y_coord}) does not exist!")
    
    def create_node(self, x_coord: int, y_coord: int, node_status: NodeStatus):
        if (x_coord, y_coord) not in self.env:
            self.env[(x_coord, y_coord)] = NodeState(Node(x_coord, y_coord), node_status)
        else:
            raise ValueError(f"Node at coordinates ({x_coord}, {y_coord}) already exists!")
        
    def get_non_task_endpoints(self) -> list[Node]:
        non_task_endpoints = []
        for _, node_state in self.env.items():
            if node_state.node_status == NodeStatus.NON_TASK_ENDPOINT.value:
                non_task_endpoints.append(node_state.node)
        return non_task_endpoints
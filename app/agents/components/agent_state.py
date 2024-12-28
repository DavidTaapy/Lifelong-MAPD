from app.components.environment.node import Node

class AgentState:

    def __init__(self, node: Node, rot: int):
        self.node = node
        self.rot = rot

    def __eq__(self, other_agent_state: "AgentState"):
        return self.node == other_agent_state.node and self.rot == other_agent_state.rot

    def __hash__(self):
        description = f"{self.node.x_coord}_{self.node.y_coord}_{self.rot}"
        hash_key = hash(description)
        return hash_key
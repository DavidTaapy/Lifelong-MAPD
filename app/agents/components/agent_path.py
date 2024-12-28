from copy import deepcopy

from app.agents.components.agent_state import AgentState

class AgentPath:

    def __init__(self, path: dict[int, AgentState] = None):
        if path is None:
            path = {}
        self.path: dict[int, AgentState] = path

    def __add__(self, other: "AgentPath"):
        new_path = self.path.copy()
        new_path.update(other.path)
        return AgentPath(new_path)

    def clone(self) -> "AgentPath":
        clone = AgentPath()
        clone.path = deepcopy(self.path)
        return clone
from app.agents.components.agent_state import AgentState
from app.components.environment.node import Node

class State:

    def __init__(self, timestep: int, state: AgentState, g_cost: int, f_cost: int):
        self.timestep = timestep
        self.state = state
        self.g_cost = g_cost
        self.f_cost = f_cost

    def __lt__(self, other_state: "State"):
        return self.f_cost < other_state.f_cost
    
    def __eq__(self, other_state: "State"):
        return self.state == other_state.state
    
    def __hash__(self):
        description = f"{self.timestep}_{self.state}_{self.g_cost}_{self.f_cost}"
        hash_key = hash(description)
        return hash_key
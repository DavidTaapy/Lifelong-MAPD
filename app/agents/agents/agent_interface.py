from abc import ABC, abstractmethod
from app.agents.components.agent_path import AgentPath
from app.agents.components.agent_state import AgentState
from app.components.system.system import System

class AgentInterface(ABC):

    @abstractmethod
    def move(self, system: System) -> System:
        pass
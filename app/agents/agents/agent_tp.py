import numpy as np

from app.agents.agents.agent_interface import AgentInterface
from app.agents.components.agent_state import AgentState
from app.agents.components.agent_path import AgentPath
from app.components.system.system import System
from app.components.environment.node import Node
from app.components.task.task import Task
from app.agents.components.search.a_star_search import A_Star_Search, heuristic

class Agent_TP(AgentInterface):

    # Class attribute to keep track of the Task IDs
    _id_counter = 0

    def __init__(self, starting_state: AgentState):
        self.id: int = self._assign_agent_id()
        self.state: AgentState = starting_state
        self.path: AgentPath = None

    def move(self, system: System) -> System:
        if system.timestep not in self.path.path:
            self.path = self.__find_path(system)
            system.agents[self.id] = self
        return system

    def __find_path(self, system: System) -> AgentPath:
        a_star = A_Star_Search(system)
        path = self.path
        curr_agent_state = path.path[system.timestep - 1]
        not_assigned_tasks = system.get_not_assigned_tasks()
        if not_assigned_tasks:
            chosen_task: Task = self.__get_nearest_task(curr_agent_state.node, not_assigned_tasks)
            chosen_task.assign(self.id)
            path += a_star.search(system.timestep, curr_agent_state, chosen_task.pickup_node)
            pickup_time = max(path.path.keys())
            chosen_task.pickup(pickup_time, self.id)
            pickup_agent_state = path.path[pickup_time]
            path += a_star.search(pickup_time + 1, pickup_agent_state, chosen_task.delivery_node)
            delivery_time = max(path.path.keys())
            chosen_task.deliver(delivery_time, self.id)
        else:
            is_task_loc = system.check_is_task_loc(curr_agent_state.node)
            in_other_agent_path = system.check_in_other_agent_path(curr_agent_state.node)
            if not is_task_loc and not in_other_agent_path:
                path += AgentPath({system.timestep: curr_agent_state})
            else:
                free_non_task_endpoints = system.get_free_non_task_endpoints()
                chosen_endpoint = self.__get_nearest_endpoint(curr_agent_state.node, free_non_task_endpoints)
                path += a_star.search(system.timestep, curr_agent_state, chosen_endpoint)
        return path

    def __get_nearest_task(self, curr_agent_node: Node, available_tasks: list[Task]) -> Task:
        h_costs = list(map(lambda task: heuristic(curr_agent_node, task.pickup_node), available_tasks))
        chosen_task = available_tasks[np.argmin(h_costs)]
        return chosen_task
    
    def __get_nearest_endpoint(self, curr_agent_node: Node, endpoints: list[Node]) -> Node:
        h_costs = list(map(lambda endpoint: heuristic(curr_agent_node, endpoint), endpoints))
        chosen_node = endpoints[np.argmin(h_costs)]
        return chosen_node

    def _assign_agent_id(self):
        curr_id = Agent_TP._id_counter
        Agent_TP._id_counter += 1
        return curr_id

import numpy as np

from app.agents.agents.agent_interface import AgentInterface
from app.agents.components.agent_state import AgentState
from app.agents.components.agent_path import AgentPath
from app.components.system.system import System
from app.components.environment.node import Node
from app.components.task.task import Task
from app.agents.components.search.a_star_search import A_Star_Search, heuristic

class Agent_TPTS(AgentInterface):

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
    
    def find_new_move(self, system: System) -> System:
        max_timestep_in_path = max(self.path.path.keys())
        while max_timestep_in_path >= system.timestep:
            del self.path.path[max_timestep_in_path]
            max_timestep_in_path -= 1
        system.agents[self.id] = self
        system = self.move(system)
        return system

    def __find_path(self, system: System) -> AgentPath:
        a_star = A_Star_Search(system)
        path = self.path
        curr_agent_state = path.path[system.timestep - 1]
        available_tasks = system.get_available_tasks()
        completed_assignment = False
        while available_tasks and not completed_assignment:
            new_path = path.clone()
            chosen_task: Task = self.__get_nearest_task(curr_agent_state.node, available_tasks)
            available_tasks.remove(chosen_task)
            new_path += a_star.search(system.timestep, curr_agent_state, chosen_task.pickup_node)
            pickup_time = max(new_path.path.keys())
            pickup_agent_state = new_path.path[pickup_time]
            new_path += a_star.search(pickup_time + 1, pickup_agent_state, chosen_task.delivery_node)
            delivery_time = max(new_path.path.keys())
            if chosen_task.assigned_agent != None:
                if delivery_time < chosen_task.delivery_time:
                    other_agent = system.get_agent(chosen_task.assigned_agent)
                    system = other_agent.find_new_move(system)
                    chosen_task.assign(self.id)
                    chosen_task.pickup(pickup_time, self.id)
                    chosen_task.deliver(delivery_time, self.id)
                    system.active_tasks[chosen_task.id] = chosen_task
                    path = new_path
                    completed_assignment = True
            else:
                chosen_task.assign(self.id)
                chosen_task.pickup(pickup_time, self.id)
                chosen_task.deliver(delivery_time, self.id)
                system.active_tasks[chosen_task.id] = chosen_task
                path = new_path
                completed_assignment = True
        if not completed_assignment:
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
        curr_id = Agent_TPTS._id_counter
        Agent_TPTS._id_counter += 1
        return curr_id

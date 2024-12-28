import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from app.agents.agents.agent_interface import AgentInterface
from app.agents.components.agent_state import AgentState
from app.agents.components.agent_path import AgentPath
from app.components.system.system import System
from app.components.environment.node import Node
from app.components.task.task import Task
from app.agents.components.search.a_star_search import A_Star_Search, heuristic

class Agent_Central(AgentInterface):

    # Class attribute to keep track of the Task IDs
    _id_counter = 0
    _last_assigned_timestep = 0

    def __init__(self, starting_state: AgentState):
        self.id: int = self._assign_agent_id()
        self.state: AgentState = starting_state
        self.path: AgentPath = None

    def move(self, system: System) -> System:
        if system.timestep > Agent_Central._last_assigned_timestep:
            task_assignment = self.assign_tasks(system)
            self.plan_paths(task_assignment, system)
            Agent_Central._last_assigned_timestep = system.timestep
        return system
    
    def plan_paths(self, task_assignment: dict, system: System):
        reassigned_agents = task_assignment.keys()
        for agent_id in reassigned_agents:
            agent = system.get_agent(agent_id)
            agent.remove_future_moves(system.timestep)
        assignment_info = [(assignment_type, agent_id, assigned) for agent_id, (assignment_type, assigned) in task_assignment.items()]
        assignment_info.sort()
        for assignment_type, agent_id, assigned in assignment_info:
            agent = system.get_agent(agent_id)
            if assignment_type == "Task":
                agent.plan_path_for_task(assigned, system)
            elif assignment_type == "Idle":
                agent.plan_path_for_idling(assigned, system)

    def plan_path_for_task(self, assigned: Task, system: System):
        a_star = A_Star_Search(system)
        path = self.path
        curr_agent_state = path.path[system.timestep - 1]
        assigned.assign(self.id)
        path += a_star.search(system.timestep, curr_agent_state, assigned.pickup_node)
        pickup_time = max(path.path.keys())
        assigned.pickup(pickup_time, self.id)
        pickup_agent_state = path.path[pickup_time]
        path += a_star.search(pickup_time + 1, pickup_agent_state, assigned.delivery_node)
        delivery_time = max(path.path.keys())
        assigned.deliver(delivery_time, self.id)      
        self.path = path

    def plan_path_for_idling(self, assigned: Node, system: System):
        a_star = A_Star_Search(system)
        path = self.path
        curr_agent_state = path.path[system.timestep - 1]
        if curr_agent_state.node == assigned:
            path += AgentPath({system.timestep: curr_agent_state})
        else:
            path += a_star.search(system.timestep, curr_agent_state, assigned)
        self.path = path
        
    def remove_future_moves(self, timestep: int):
        max_path_timestep = max(self.path.path.keys())
        while max_path_timestep >= timestep:
            del self.path.path[max_path_timestep]
            max_path_timestep -= 1
    
    def assign_tasks(self, system: System):
        free_agents = []
        executed_tasks = system.get_executed_tasks()
        executing_agents = list(map(lambda task: task.assigned_agent, executed_tasks))
        for agent in system.agents:
            if agent.id not in executing_agents:
                free_agents.append(agent.id)

        endpoints, num_task_endpoints = self.get_endpoints(system, free_agents)
        c = len(free_agents)
        pickup_locs = []
        for endpoint in endpoints:
            if type(endpoint) == Task:
                pickup_locs.append(endpoint.pickup_node)
            else:
                pickup_locs.append(endpoint)
        
        h_costs = {}
        max_h_cost = 0
        for endpoint in pickup_locs:
            h_costs[endpoint] = {}
            for id in free_agents:
                agent = system.get_agent(id)
                agent_state = agent.path.path[system.timestep - 1]
                curr_h_cost = heuristic(agent_state.node, endpoint)
                h_costs[endpoint][id] = curr_h_cost
                max_h_cost = max(max_h_cost, curr_h_cost)
        C = max_h_cost + 1
        
        modified_cost = {}
        for i in range(len(pickup_locs)):
            endpoint = pickup_locs[i]
            modified_cost[endpoint] = []
            if i < num_task_endpoints:
                for id in free_agents:
                    modified_cost[endpoint].append(c * C * h_costs[endpoint][id])
            else:
                for id in free_agents:
                    modified_cost[endpoint].append(c * C ** 2 + h_costs[endpoint][id])
        modified_df = pd.DataFrame.from_dict(modified_cost, orient="index", columns=free_agents)
        
        row_ind, col_ind = linear_sum_assignment(modified_df)
        assignment_results = {}
        for i in range(c):
            curr_agent_id = free_agents[col_ind[i]]
            if i < num_task_endpoints:
                curr_task = endpoints[row_ind[i]]
                assignment_results[curr_agent_id] = ("Task", curr_task)
            else:
                curr_loc = pickup_locs[row_ind[i]]
                assignment_results[curr_agent_id] = ("Idle", curr_loc)

        return assignment_results

    def get_endpoints(self, system: System, free_agents: list[int]):
        pickup_locs = []
        avoid_locs = []
        executed_tasks = system.get_executed_tasks()
        for task in executed_tasks:
            avoid_locs.append(task.delivery_node)
        unexecuted_tasks = system.get_unexecuted_tasks()
        for task in unexecuted_tasks:
            if (task.pickup_node not in avoid_locs) and (task.delivery_node not in avoid_locs):
                pickup_locs.append(task)
                avoid_locs.append(task.pickup_node)
                avoid_locs.append(task.delivery_node)
        num_task_endpoints = len(pickup_locs)
        num_free_agents = len(free_agents)
        if num_task_endpoints < num_free_agents:
            all_endpoints = system.get_free_non_task_endpoints()
            free_endpoints = [endpoint for endpoint in all_endpoints if endpoint not in avoid_locs]
            for id in free_agents:
                agent = system.get_agent(id)
                agent_state = agent.path.path[system.timestep - 1]
                h_costs = list(map(lambda x: heuristic(agent_state.node, x), free_endpoints))
                chosen_endpoint = free_endpoints[np.argmin(h_costs)]
                pickup_locs.append(chosen_endpoint)
                free_endpoints.remove(chosen_endpoint)
        return pickup_locs, num_task_endpoints

    def _assign_agent_id(self):
        curr_id = Agent_Central._id_counter
        Agent_Central._id_counter += 1
        return curr_id

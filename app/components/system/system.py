from app.components.environment.map import Map
from app.components.environment.node import Node
from app.components.task.task import Task
from app.agents.components.agent_path import AgentPath

class System():

    def __init__(self, map: Map, tasks: list[Task], agents):
        self.map: Map = map
        self.tasks: list[Task] = tasks
        self.timestep: int = 0
        self.active_tasks: dict[int, Task] = {}
        self.agents: list = self.__generate_paths(agents)
        self.__initialize_system()

    def iterate(self) -> "System":
        self.timestep += 1
        self.__check_agent_paths()
        self.__check_tasks(self.timestep)
        return self
    
    def get_agent(self, agent_id: int):
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def get_not_assigned_tasks(self) -> list[Task]:
        not_assigned_tasks = []
        for task in self.active_tasks.values():
            if task.assigned_agent is None:
                not_assigned_tasks.append(task)
        return not_assigned_tasks
    
    def get_available_tasks(self) -> list[Task]:
        available_tasks = []
        for task in self.active_tasks.values():
            if not task.assigned_agent or task.pickup_time > self.timestep:
                available_tasks.append(task)
        return available_tasks
    
    def get_executed_tasks(self) -> list[Task]:
        executed_tasks = []
        for task in self.active_tasks.values():
            if task.assigned_agent and task.pickup_time <= self.timestep:
                executed_tasks.append(task)
        return executed_tasks
    
    def get_unexecuted_tasks(self) -> list[Task]:
        unexecuted_tasks = []
        for task in self.active_tasks.values():
            if task.assigned_agent == None or task.pickup_time > self.timestep:
                unexecuted_tasks.append(task)
        return unexecuted_tasks
    
    def check_is_task_loc(self, node: Node) -> bool:
        for _, task in self.active_tasks.items():
            if task.delivery_node == node or task.pickup_node == node:
                return True
        return False
    
    def check_in_other_agent_path(self, node: Node) -> bool:
        for agent in self.agents:
            agent_path = agent.path
            len_timestep = len(agent_path.path)
            for timestep in range(self.timestep, len_timestep):
                if node == agent_path.path[timestep].node:
                    return True
        return False
    
    def get_free_non_task_endpoints(self) -> list[Node]:
        non_task_endpoints = self.map.get_non_task_endpoints()
        agent_last_nodes = self.__get_agent_last_nodes()
        free_non_task_endpoints = [endpoint for endpoint in non_task_endpoints if endpoint not in agent_last_nodes]
        return free_non_task_endpoints

    def __get_agent_last_nodes(self) -> list[Node]:
        last_nodes = []
        for agent in self.agents:
            agent_path = agent.path
            last_node = agent_path.path[max(agent_path.path.keys())].node
            last_nodes.append(last_node)
        return last_nodes

    def __check_agent_paths(self):
        for agent in self.agents:
            agent.move(self)
    
    def __check_tasks(self, next_timestep: int):
        for task_id in range(len(self.tasks)):
            curr_task = self.tasks[task_id]
            if next_timestep == curr_task.add_time:
                self.active_tasks[task_id] = curr_task
        completed_tasks = []
        for task_id, task in self.active_tasks.items():
            if next_timestep == task.pickup_time:
                task.has_been_picked_up = True
            if next_timestep == task.delivery_time:
                completed_tasks.append(task_id)
        for task_id in completed_tasks:
            del self.active_tasks[task_id]
    
    def __generate_paths(self, agents) -> list:
        for i in range(len(agents)):
            agent_start_state = agents[i].state
            agent_start_path = AgentPath()
            agent_start_path.path[0] = agent_start_state
            agents[i].path = agent_start_path
        return agents

    def __initialize_system(self):
        self.__check_tasks(next_timestep=0)

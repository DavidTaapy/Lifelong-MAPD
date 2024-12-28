from random import randrange

from app.agents.agents.agent_interface import AgentInterface
from app.agents.components.agent_state import AgentState
from app.components.environment.node import Node
from app.components.environment.node_state import NodeStatus
from app.components.environment.map import Map
from app.components.task.task import Task
from app.graphics.gui import GUI
from app.components.system.system import System

from app.agents.agents.agent_tp import Agent_TP
from app.agents.agents.agent_tpts import Agent_TPTS
from app.agents.agents.agent_central import Agent_Central

class App:

    def __init__(self, agent_class: AgentInterface, num_agents: int, num_tasks: int, num_tasks_per_timestep: int):
        self.agent_class: AgentInterface = agent_class
        self.num_agents: int = num_agents
        self.num_tasks: int = num_tasks
        self.num_tasks_per_timestep: int = num_tasks_per_timestep
        self.map: Map = self.__generate_map()
        self.agents: list[AgentInterface] = self.__generate_agents()
        self.tasks: list[Task] = self.__generate_tasks()
        self.system: System = System(self.map, self.tasks, self.agents)

    def __generate_map(self) -> Map:
        node_status: list[list[int]] = []
        for y_coord in range(21):
            if y_coord in [0, 20]:
                node_status.append(["FREE"] * 35)
            elif y_coord in list(range(1, 21, 2)):
                node_status.append(["FREE", "NON_TASK_ENDPOINT", "NON_TASK_ENDPOINT"] * 2 + (["FREE"] + ["TASK_ENDPOINT"] * 10) * 2 + ["FREE", "NON_TASK_ENDPOINT", "NON_TASK_ENDPOINT"] * 2 + ["FREE"])
            elif y_coord in list(range(2, 21, 4)):
                node_status.append(["FREE", "NON_TASK_ENDPOINT", "NON_TASK_ENDPOINT"] * 2 + (["FREE"] + ["OBSTACLE"] * 10) * 2 + ["FREE", "NON_TASK_ENDPOINT", "NON_TASK_ENDPOINT"] * 2 + ["FREE"])
            else:
                node_status.append(["FREE", "NON_TASK_ENDPOINT", "NON_TASK_ENDPOINT"] * 2 + (["FREE"] * 11) * 2 + ["FREE", "NON_TASK_ENDPOINT", "NON_TASK_ENDPOINT"] * 2 + ["FREE"])
        map = Map()
        for y_coord in range(len(node_status)):
            for x_coord in range(len(node_status[0])):
                map.create_node(x_coord=x_coord, y_coord=y_coord, node_status=node_status[y_coord][x_coord])
        return map
    
    def __generate_agents(self) -> list[AgentInterface]:
        spawn_loc = []
        for y_coord in range(1, 20):
            for x_coord in [1, 2, 4, 5, 29, 30, 32, 33]:
                spawn_loc.append((x_coord, y_coord))
        agents = []
        for _ in range(self.num_agents):
            rand_x, rand_y = spawn_loc.pop(randrange(len(spawn_loc)))
            rand_degree = randrange(0, 4) * 90
            agent_state = AgentState(node=Node(rand_x, rand_y), rot=rand_degree)
            agents.append(self.agent_class(agent_state))
        return agents
    
    def __generate_tasks(self) -> list[Task]:
        task_endpoints = self.__get_task_spawn_nodes()
        tasks = []
        timestep = 0
        tasks_added = 0
        while tasks_added < self.num_tasks:
            task_to_release = (timestep + 1) * self.num_tasks_per_timestep
            if tasks_added >= task_to_release:
                timestep += 1
                continue
            pickup_loc = randrange(len(task_endpoints))
            delivery_loc = randrange(len(task_endpoints))
            while delivery_loc == pickup_loc:
                delivery_loc = randrange(len(task_endpoints))
            tasks.append(Task(pickup_node=task_endpoints[pickup_loc], delivery_node=task_endpoints[delivery_loc], add_time=timestep))
            tasks_added += 1  
        return tasks
    
    def __get_task_spawn_nodes(self) -> list[Node]:
        task_nodes = []
        for _, node_state in self.map.env.items():
            if node_state.node_status == NodeStatus.TASK_ENDPOINT.value:
                task_nodes.append(node_state.node)
        return task_nodes
    
    def run_simulation(self):
        GUI(self.system)
            
if __name__ == "__main__":
    app = App(agent_class=Agent_TP, num_agents=3, num_tasks=15, num_tasks_per_timestep=0.25)
    app.run_simulation()

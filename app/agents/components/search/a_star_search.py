from heapq import heappop, heappush

from app.components.system.system import System
from app.components.environment.node import Node
from app.agents.components.agent_state import AgentState
from app.agents.components.agent_path import AgentPath
from app.agents.components.search.components.state import State
from app.components.environment.node_state import NodeStatus

__all__ = ["heuristic", "A_Star_Search"]

# Heuristic function used in A* Search - Manhattan Distance
def heuristic(start_node: Node, end_node: Node):
    return abs(start_node.x_coord - end_node.x_coord) + abs(start_node.y_coord - end_node.y_coord)

class A_Star_Search:

    def __init__(self, system: System):
        self.system: System = system

    def search(self, timestep: int, start_state: AgentState, end_node: Node) -> AgentPath:
        init_state = State(timestep - 1, start_state, 0, heuristic(start_state.node, end_node))
        prior_queue: list[State] = [init_state]
        came_from_dict = {}  
        visited = []
        while prior_queue:
            curr_state = heappop(prior_queue)
            if curr_state.state.node == end_node:
                path = [curr_state]
                if curr_state in came_from_dict:
                    while curr_state in came_from_dict:
                        curr_state = came_from_dict[curr_state]
                        path.append(curr_state)
                    path = path[::-1]
                path = {agent_state.timestep: agent_state.state for agent_state in path}
                return AgentPath(path)
            visited.append(curr_state)
            neighbours = self.__get_neighbours(curr_state, end_node)
            for neigh_state in neighbours:
                if (neigh_state not in visited) and (neigh_state not in prior_queue):
                    came_from_dict[neigh_state] = curr_state
                    heappush(prior_queue, neigh_state)
        return None

    def __check_collision(self, curr_state: State, next_state: State):
        for agent in self.system.agents:
            agent_path = agent.path
            if next_state.timestep in agent_path.path:
                other_next_state: AgentState = agent_path.path[next_state.timestep]
                if next_state.state.node == other_next_state.node:
                    return True
                other_curr_time = agent_path.path[curr_state.timestep]
                if other_next_state.node == curr_state.state.node and other_curr_time.node == next_state.state.node:
                    return True
        return False

    def __check_valid_state(self, curr_state: State, next_state: State):
        next_node = next_state.state.node
        try:
            node_status = self.system.map.env[(next_node.x_coord, next_node.y_coord)].node_status
            is_obstacle = True if node_status == NodeStatus.OBSTACLE.value else False
        except:
            return False
        return (next_state.state.node.is_in_boundary()) \
             and (not is_obstacle) and (not self.__check_collision(curr_state, next_state))

    def __get_neighbours(self, curr_state: State, end_node: Node) -> list[State]:
        neigh_states = []
        neigh_timestep = curr_state.timestep + 1
        curr_node = curr_state.state.node
        curr_y_coord = curr_node.y_coord
        curr_x_coord = curr_node.x_coord
        curr_rot = curr_state.state.rot
        dir_dict = {
            0: Node(curr_x_coord, curr_y_coord - 1),
            90: Node(curr_x_coord + 1, curr_y_coord),
            180: Node(curr_x_coord, curr_y_coord + 1),
            270: Node(curr_x_coord - 1, curr_y_coord)
        }
        new_g_cost = curr_state.g_cost + 1
        poss_neigh = [State(neigh_timestep, AgentState(Node(curr_x_coord, curr_y_coord), curr_rot), new_g_cost, heuristic(Node(curr_x_coord, curr_y_coord), end_node)),
                      State(neigh_timestep, AgentState(Node(curr_x_coord, curr_y_coord), (curr_rot + 90) % 360), new_g_cost, heuristic(Node(curr_x_coord, curr_y_coord), end_node)),
                      State(neigh_timestep, AgentState(Node(curr_x_coord, curr_y_coord), (curr_rot - 90) % 360), new_g_cost, heuristic(Node(curr_x_coord, curr_y_coord), end_node)),
                      State(neigh_timestep, AgentState(dir_dict[curr_rot], curr_rot), new_g_cost, heuristic(dir_dict[curr_rot], end_node))]
        for neigh_state in poss_neigh:
            if self.__check_valid_state(curr_state, neigh_state):
                neigh_states.append(neigh_state)
        return neigh_states
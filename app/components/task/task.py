from app.components import Node

class Task:

    # Class attribute to keep track of the Task IDs
    _id_counter = 0

    def __init__(self, pickup_node: Node, delivery_node: Node, add_time: int):
        self.id: int = self._assign_task_id()
        self.pickup_node: Node = pickup_node
        self.delivery_node: Node = delivery_node
        self.add_time: int = add_time
        self.pickup_time: int | None = None
        self.delivery_time: int | None = None
        self.assigned_agent: int | None = None
        self.has_been_picked_up: bool = False

    def pickup(self, pickup_time: int, agent_id: int) -> "Task":
        if self.assigned_agent != agent_id:
            raise ValueError(f"Agent {agent_id} is not the assigned agent for task {self.id}")
        self.pickup_time = pickup_time
        return self
    
    def deliver(self, delivery_time: int, agent_id: int) -> "Task":
        if self.assigned_agent != agent_id:
            raise ValueError(f"Agent {agent_id} is not the assigned agent for task {self.id}")
        self.delivery_time = delivery_time
        return self
    
    def assign(self, agent_id: int) -> "Task":
        self.assigned_agent = agent_id
        return self
    
    def _assign_task_id(self):
        curr_id = Task._id_counter
        Task._id_counter += 1
        return curr_id


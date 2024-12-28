from app.constants import MAX_COLS, MAX_ROWS

class Node:

    def __init__ (self, x_coord: int, y_coord: int):
        self.x_coord: int = x_coord
        self.y_coord: int = y_coord

    def __eq__(self, other_node: "Node") -> bool:
        if not isinstance(other_node, Node):
            raise TypeError(f"Cannot compare 'Node' with '{type(other_node).__name__}'")
        return (self.x_coord == other_node.x_coord) and (self.y_coord == other_node.y_coord)
    
    def is_in_boundary(self):
        return 0 <= self.x_coord < MAX_COLS and 0 <= self.y_coord < MAX_ROWS

    def __hash__(self):
        hash_prime = 397
        hash_key = (((self.x_coord * hash_prime) ** self.y_coord) * hash_prime)
        return hash_key

import PySimpleGUI as sg
from app.agents.components.agent_path import AgentPath
from app.agents.components.agent_state import AgentState
from app.components.system import System
from app.components.task import Task
from app.components.environment.map import Map
from app.components.environment.node_state import NodeStatus
from app.constants import MAX_ROWS, MAX_COLS

CELL_SIZE = 30
APP_FONT = "Any 16"
THEME = "DarkGrey5"

CELL_COLOR_MAP = {
    NodeStatus.FREE.value: "",
    NodeStatus.NON_TASK_ENDPOINT.value: "LIGHTBLUE",
    NodeStatus.TASK_ENDPOINT.value: "LIGHTGREEN",
    NodeStatus.OBSTACLE.value: "GREY"
}

class GUI():

    def __init__(self, system: System):
        self.system = system
        self._VARS = self.__initialize_variables()
        self.__draw_canvas()
        self.__update_map()
        self.__event_loop()

    def __initialize_variables(self):
        return {
            'xCellCount': MAX_COLS,
            'yCellCount': MAX_ROWS,
            'canvas': None,
            'window': None
        }

    def __draw_canvas(self):
        layout = [
            [sg.Canvas(size=(self._VARS["xCellCount"] * CELL_SIZE, self._VARS["yCellCount"] * CELL_SIZE), background_color="white", key="canvas")],
            [
                sg.Exit(font=APP_FONT),
                sg.Text("Timestep: 0", key="-Exit-", font=APP_FONT, size=(15, 1))
            ]
        ]
        self._VARS["window"] = sg.Window("Simulation", layout, resizable=True, finalize=True, return_keyboard_events=True)
        self._VARS["canvas"] = self._VARS["window"]["canvas"]

    def __draw_grid(self):
        xCanvasSize = self._VARS["xCellCount"] * CELL_SIZE
        yCanvasSize = self._VARS["yCellCount"] * CELL_SIZE
        for x in range(self._VARS["xCellCount"]):
            xCoord = CELL_SIZE * x
            self._VARS["canvas"].TKCanvas.create_line(
                (xCoord, 0), (xCoord, yCanvasSize), fill="BLACK", width=1
            )
        for y in range(self._VARS["yCellCount"]):
            yCoord = CELL_SIZE * y
            self._VARS["canvas"].TKCanvas.create_line(
                (0, yCoord), (xCanvasSize, yCoord), fill="BLACK", width=1
            )

    def __draw_cell(self, x: int, y: int, color: str):
        x *= CELL_SIZE
        y *= CELL_SIZE
        self._VARS['canvas'].TKCanvas.create_rectangle(
            x, y, x + CELL_SIZE, y + CELL_SIZE, outline='BLACK', fill=color, width=1
        )

    def __mark_cells(self):
        for (x_coord, y_coord), node_state in self.system.map.env.items():
            self.__draw_cell(x_coord, y_coord, CELL_COLOR_MAP[node_state.node_status])

    def __populate_agents(self):
        for agent in self.system.agents:
            agent_path = agent.path
            curr_agent_state: AgentState = agent_path.path[self.system.timestep]
            self.__draw_agent_cell(curr_agent_state)

    def __draw_agent_cell(self, agent_state: AgentState):
        xCoord = agent_state.node.x_coord * CELL_SIZE
        yCoord = agent_state.node.y_coord * CELL_SIZE
        if agent_state.rot == 0:
            points = [xCoord + 0.1 * CELL_SIZE, yCoord + 0.9 * CELL_SIZE, xCoord + 0.9 * CELL_SIZE, yCoord + 0.9 * CELL_SIZE, xCoord + 0.5 * CELL_SIZE, yCoord + 0.1 * CELL_SIZE]
        elif agent_state.rot == 90:
            points = [xCoord + 0.1 * CELL_SIZE, yCoord + 0.1 * CELL_SIZE, xCoord + 0.1 * CELL_SIZE, yCoord + 0.9 * CELL_SIZE, xCoord + 0.9 * CELL_SIZE, yCoord + 0.5 * CELL_SIZE]
        elif agent_state.rot == 180:
            points = [xCoord + 0.1 * CELL_SIZE, yCoord + 0.1 * CELL_SIZE, xCoord + 0.9 * CELL_SIZE, yCoord + 0.1 * CELL_SIZE, xCoord + 0.5 * CELL_SIZE, yCoord + 0.9 * CELL_SIZE]
        elif agent_state.rot == 270:
            points = [xCoord + 0.1 * CELL_SIZE, yCoord + 0.5 * CELL_SIZE, xCoord + 0.9 * CELL_SIZE, yCoord + 0.1 * CELL_SIZE, xCoord + 0.9 * CELL_SIZE, yCoord + 0.9 * CELL_SIZE]
        self._VARS["canvas"].TKCanvas.create_polygon(points, fill='BLACK')

    def __populate_tasks(self):
        for task in self.system.active_tasks.values():
            self.__draw_task_cell(task)

    def __draw_task_cell(self, task: Task):
        self.__draw_cell(task.delivery_node.x_coord, task.delivery_node.y_coord, 'RED')
        if not task.has_been_picked_up:
            self.__draw_cell(task.pickup_node.x_coord, task.pickup_node.y_coord, 'ORANGE')

    def __update_map(self):
        self._VARS['canvas'].TKCanvas.delete("all")
        self.__draw_grid()
        self.__update_timestep()
        self.__mark_cells()
        self.__populate_tasks()
        self.__populate_agents()

    def __update_timestep(self):
        self._VARS['window']['-Exit-'].update(f"Timestep: {self.system.timestep}")

    def __event_loop(self):
        while True:
            event, _ = self._VARS["window"].read()
            if event in (sg.WIN_CLOSED, "Exit"):
                break
            self.system = self.system.iterate()
            self.__update_map()
        self.__close_window()

    def __close_window(self):
        self._VARS['window'].close()

if __name__ == "__main__":
    GUI()
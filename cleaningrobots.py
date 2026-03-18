import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time
import json

# -----------------------------
# House Layout
# -----------------------------
house = {
    "Living Room": {"pos": (0, 1), "vacuumed": False, "mopped": False, "trash_collected": False},
    "Kitchen": {"pos": (1, 1), "vacuumed": False, "mopped": False, "trash_collected": False},
    "Bedroom": {"pos": (0, 0), "vacuumed": False, "mopped": False, "trash_collected": False},
    "Bathroom": {"pos": (1, 0), "vacuumed": False, "mopped": False, "trash_collected": False},
    "Hallway": {"pos": (0.5, 2), "vacuumed": False, "mopped": False, "trash_collected": False}
}

# -----------------------------
# Memory Initialization
# -----------------------------
memory = {
    "VacuumBot": {},
    "MopBot": {},
    "TrashBot": {}
}

skipped_rooms = []  # Keep track of skipped rooms

# -----------------------------
# Robot Class
# -----------------------------
class Robot:
    def __init__(self, name, task, color):
        self.name = name
        self.task = task
        self.color = color
        self.current_room = None

    def move_to_room(self, room):
        self.current_room = room

    def perform_task(self, room):
        if self.task == "vacuum":
            house[room]["vacuumed"] = True
        elif self.task == "mop":
            if house[room]["vacuumed"]:
                house[room]["mopped"] = True
            else:
                return False
        elif self.task == "trash":
            house[room]["trash_collected"] = True
        return True

# -----------------------------
# Initialize Robots
# -----------------------------
vacuum_robot = Robot("VacuumBot", "vacuum", "blue")
mop_robot = Robot("MopBot", "mop", "green")
trash_robot = Robot("TrashBot", "trash", "red")
robots = [vacuum_robot, mop_robot, trash_robot]

# -----------------------------
# Matplotlib Setup
# -----------------------------
plt.ion()
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
ax.set_xlim(-0.5, 1.5)
ax.set_ylim(-0.5, 2.8)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Smart Interactive House Cleaning Simulation")

# Draw rooms
for room, info in house.items():
    x, y = info["pos"]
    ax.add_patch(plt.Rectangle((x-0.25, y-0.25), 0.5, 0.5, fill=None, edgecolor='black'))
    ax.text(x, y+0.15, room, ha='center', fontsize=8)

# Robot markers and instruction
robot_markers = []
instruction_text = ax.text(0.5, 2.6, "", ha='center', fontsize=10, color='purple')

# -----------------------------
# Button Setup
# -----------------------------
button_pressed = None
def on_yes(event):
    global button_pressed
    button_pressed = True
def on_no(event):
    global button_pressed
    button_pressed = False

ax_yes = plt.axes([0.3, 0.05, 0.1, 0.075])
ax_no = plt.axes([0.6, 0.05, 0.1, 0.075])
btn_yes = Button(ax_yes, 'Yes')
btn_no = Button(ax_no, 'No')
btn_yes.on_clicked(on_yes)
btn_no.on_clicked(on_no)

# -----------------------------
# Helper Functions
# -----------------------------
def plot_robots(instruction=""):
    # Remove old markers
    for marker in robot_markers:
        marker.remove()
    robot_markers.clear()
    
    # Draw robots
    for robot in robots:
        if robot.current_room:
            x, y = house[robot.current_room]["pos"]
            marker, = ax.plot(x, y, 'o', color=robot.color, markersize=15)
            robot_markers.append(marker)
    
    # Update instruction
    instruction_text.set_text(instruction)
    plt.draw()
    plt.pause(0.1)

def ask_permission(robot, room):
    global button_pressed
    # Check memory first
    if room in memory[robot.name]:
        allowed = memory[robot.name][room]
        plot_robots(f"{robot.name} remembers decision for {room}: {'Yes' if allowed else 'No'}")
        plt.pause(0.5)
        return allowed
    
    # Ask user with buttons
    plot_robots(f"{robot.name}: Can I clean the {room}? Click Yes/No")
    button_pressed = None
    while button_pressed is None:
        plt.pause(0.1)
    
    memory[robot.name][room] = button_pressed
    return button_pressed

# -----------------------------
# Interactive Cleaning Loop
# -----------------------------
rooms = list(house.keys())

def clean_room_sequence(room):
    # Vacuum
    if ask_permission(vacuum_robot, room):
        vacuum_robot.move_to_room(room)
        vacuum_robot.perform_task(room)
        plot_robots(f"{vacuum_robot.name} vacuumed {room}")
    else:
        plot_robots(f"{vacuum_robot.name} skipped {room}")
        skipped_rooms.append(room)
        return  # skip mop/trash

    # Mop
    if ask_permission(mop_robot, room):
        mop_robot.move_to_room(room)
        while not mop_robot.perform_task(room):
            plot_robots(f"{mop_robot.name} waiting for vacuum in {room}")
            plt.pause(0.5)
        plot_robots(f"{mop_robot.name} mopped {room}")
    else:
        plot_robots(f"{mop_robot.name} skipped {room}")

    # Trash
    if ask_permission(trash_robot, room):
        trash_robot.move_to_room(room)
        trash_robot.perform_task(room)
        plot_robots(f"{trash_robot.name} collected trash in {room}")
    else:
        plot_robots(f"{trash_robot.name} skipped {room}")

# First pass
for room in rooms:
    clean_room_sequence(room)

# Ask skipped rooms again at the end
if skipped_rooms:
    plot_robots("Asking skipped rooms again...")
    time.sleep(1)
    for room in skipped_rooms.copy():
        clean_room_sequence(room)
        skipped_rooms.remove(room)

# -----------------------------
# End of Simulation
# -----------------------------
plt.ioff()
plt.show()

# Final Status
print("\nFinal Room Status:")
for room, status in house.items():
    print(f"{room}: {status}")

# Optional: save memory for next session
with open("robot_memory.json", "w") as f:
    json.dump(memory, f)
print("\nMemory saved to robot_memory.json")
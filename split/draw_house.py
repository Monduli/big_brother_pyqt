from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt5.QtGui import QBrush, QPen, QColor, QFont
import random

class HouseGuestItem(QGraphicsItem):
    def __init__(self, initials, position, color, parent=None):
        super().__init__(parent)
        self.initials = initials
        self.color = color
        self.setPos(position)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)  # Make item non-focusable

    def boundingRect(self):
        return QRectF(-25, -25, 50, 50)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(-25, -25, 50, 50)
        font = QFont()
        font.setPointSize(16)
        painter.setFont(font)
        painter.drawText(QRectF(-25, -25, 50, 50), Qt.AlignCenter, self.initials)

class BigBrotherHouse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Big Brother House")
        self.setGeometry(100, 100, 1000, 800)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.create_house()
        self.add_houseguests()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_houseguests)
        self.timer.start(1000)  # Move houseguests every 1 second

    def create_house(self):
        # Define the dimensions of the house and the grid
        house_width = self.width() - 20  # Adjust the house width to fit within the window
        house_height = self.height() - 20  # Adjust the house height to fit within the window
        self.grid_size = 100  # Each grid cell is 100x100

        # Calculate the number of grid cells
        num_cols = house_width // self.grid_size
        num_rows = house_height // self.grid_size

        # Create a 2D list to represent the grid
        self.grid = [[0 for _ in range(num_cols)] for _ in range(num_rows)]

        # Define room presets
        room_presets = [
            (2, 2),  # Small room (2x2 cells)
            (3, 2),  # Medium room (3x2 cells)
            (3, 3),  # Large room (3x3 cells)
            (4, 4),  # XL room (4x4 cells)
        ]

        # Generate rooms in the grid
        self.rooms = []
        num_rooms = random.randint(5, 10)  # Generate a random number of rooms
        for _ in range(num_rooms):
            # Choose a random room preset
            preset = random.choice(room_presets)
            room_cols, room_rows = preset

            # Find an empty space in the grid for the room
            found_space = False
            max_attempts = 100  # Maximum number of attempts to find an empty space
            attempts = 0
            while not found_space and attempts < max_attempts:
                col = random.randint(0, num_cols - room_cols)
                row = random.randint(0, num_rows - room_rows)
                if all(self.grid[r][c] == 0 for r in range(row, row + room_rows) for c in range(col, col + room_cols)):
                    # Mark the cells as occupied by the room
                    for r in range(row, row + room_rows):
                        for c in range(col, col + room_cols):
                            self.grid[r][c] = 1
                    found_space = True
                else:
                    attempts += 1

            if found_space:
                # Create a room based on the grid cells
                room_x = col * self.grid_size + 10  # Add offset to center the house within the window
                room_y = row * self.grid_size + 10  # Add offset to center the house within the window
                room_width = room_cols * self.grid_size
                room_height = room_rows * self.grid_size
                room = QGraphicsRectItem(room_x, room_y, room_width, room_height)
                room.setBrush(QBrush(Qt.gray))  # Room color
                room.setPen(QPen(Qt.black, 2))
                self.rooms.append(room)
                self.scene.addItem(room)

        # Connect rooms with hallways and doors
        self.connect_rooms()

    def connect_rooms(self):
        # Connect rooms with hallways and doors
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]

            # Find the closest walls between the two rooms
            min_distance = float('inf')
            closest_walls = None
            for x1, y1, w1, h1 in [(room1.rect().x(), room1.rect().y(), room1.rect().width(), 0),
                                   (room1.rect().x(), room1.rect().y(), 0, room1.rect().height()),
                                   (room1.rect().x(), room1.rect().y() + room1.rect().height(), room1.rect().width(), 0),
                                   (room1.rect().x() + room1.rect().width(), room1.rect().y(), 0, room1.rect().height())]:
                for x2, y2, w2, h2 in [(room2.rect().x(), room2.rect().y(), room2.rect().width(), 0),
                                       (room2.rect().x(), room2.rect().y(), 0, room2.rect().height()),
                                       (room2.rect().x(), room2.rect().y() + room2.rect().height(), room2.rect().width(), 0),
                                       (room2.rect().x() + room2.rect().width(), room2.rect().y(), 0, room2.rect().height())]:
                    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        closest_walls = ((x1, y1, w1, h1), (x2, y2, w2, h2))

            # Add a hallway and door between the closest walls
            if closest_walls:
                (x1, y1, w1, h1), (x2, y2, w2, h2) = closest_walls
                hallway_x = min(x1, x2)
                hallway_y = min(y1, y2)
                hallway_width = abs(x1 - x2) + max(w1, w2)
                hallway_height = abs(y1 - y2) + max(h1, h2)
                hallway = QGraphicsRectItem(hallway_x, hallway_y, hallway_width, hallway_height)
                hallway.setBrush(QBrush(Qt.lightGray))  # Hallway color
                hallway.setPen(QPen(Qt.black, 2))
                self.scene.addItem(hallway)

                # Add a door between the rooms
                door_x = min(x1 + w1 // 2, x2 + w2 // 2) - 10
                door_y = min(y1 + h1 // 2, y2 + h2 // 2) - 10
                door_width = 20
                door_height = 20
                door = QGraphicsRectItem(door_x, door_y, door_width, door_height)
                door.setBrush(QBrush(Qt.darkGreen))
                self.scene.addItem(door)
                self.doors = [door]
                
    def get_unique_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return QColor(r, g, b)

    def add_houseguests(self):
        # Define a list of colors for the houseguests
        self.houseguests = []
        colors = [Qt.red, Qt.green, Qt.blue, Qt.yellow, Qt.cyan, Qt.magenta, Qt.darkYellow]
        num_hg = 7
        spawns = []
        for x in range(num_hg):
            pos = self.get_random_position_in_room(self.rooms[random.randint(0,len(self.rooms)-1)])
            if pos not in spawns:
                spawns.append(pos)
                initials = f"{chr(65 + x)}{chr(65 + x)}"  # Generate AA, BB, CC, etc.
                color = self.get_unique_color()
                self.houseguests.append(HouseGuestItem(initials, pos, color))
                self.scene.addItem(self.houseguests[-1])
                
        """ 
        # Add houseguests to the scene
        self.houseguests = [
            HouseGuestItem("AA", self.get_random_position_in_room(self.rooms[0]), colors[0]),
            HouseGuestItem("BB", self.get_random_position_in_room(self.rooms[1]), colors[1]),
            HouseGuestItem("CC", self.get_random_position_in_room(self.rooms[2]), colors[2]),
            HouseGuestItem("DD", self.get_random_position_in_room(self.rooms[3]), colors[3]),
            HouseGuestItem("EE", self.get_random_position_in_room(self.rooms[4]), colors[4]),
            HouseGuestItem("FF", self.get_random_position_in_room(self.rooms[5]), colors[5]),
            HouseGuestItem("GG", self.get_random_position_in_room(self.rooms[6]), colors[6])
        ] """

        for hg in self.houseguests:
            self.scene.addItem(hg)

    def move_houseguests(self):
        for hg in self.houseguests:
            current_pos = hg.pos()
            current_row = int((current_pos.y() - 10) // 100)
            current_col = int((current_pos.x() - 10) // 100)

            # Check if the current position is within the house boundaries
            if 0 <= current_row < len(self.grid) and 0 <= current_col < len(self.grid[0]):
                # Check if the current position is valid (inside a room or on a door)
                if self.grid[current_row][current_col] == 1 or any(door.contains(current_pos) for door in self.doors):
                    # Find adjacent unoccupied positions
                    adjacent_positions = []
                    for row, col in [(current_row - 1, current_col), (current_row + 1, current_col), (current_row, current_col - 1), (current_row, current_col + 1)]:
                        if (
                            0 <= row < len(self.grid)
                            and 0 <= col < len(self.grid[0])
                            and (self.grid[row][col] == 1 or any(door.contains(QPointF(col * 100 + 60, row * 100 + 60)) for door in self.doors))
                        ):
                            new_pos = QPointF(col * 100 + 60, row * 100 + 60)  # Center the houseguest within the grid square
                            if not any(hg.pos() == new_pos for hg in self.houseguests):
                                adjacent_positions.append(new_pos)

                    # Move the houseguest to a random adjacent unoccupied position
                    if adjacent_positions:
                        new_pos = random.choice(adjacent_positions)
                        hg.setPos(new_pos)
                    else:
                        # If there are no valid adjacent positions, keep the houseguest in the current position
                        hg.setPos(current_pos)
                else:
                    # If the current position is not valid, move the houseguest to a random valid position
                    valid_positions = []
                    for room in self.rooms:
                        valid_positions.extend([self.get_random_position_in_room(room) for _ in range(10)])
                    if valid_positions:
                        new_pos = random.choice(valid_positions)
                        hg.setPos(new_pos)
            else:
                # If the houseguest is outside the house boundaries, move them to a random valid position
                valid_positions = []
                for room in self.rooms:
                    valid_positions.extend([self.get_random_position_in_room(room) for _ in range(10)])
                if valid_positions:
                    new_pos = random.choice(valid_positions)
                    hg.setPos(new_pos)

    def get_random_position_in_room(self, room):
        x = random.uniform(room.rect().x() + 25, room.rect().x() + room.rect().width() - 25)
        y = random.uniform(room.rect().y() + 25, room.rect().y() + room.rect().height() - 25)
        return QPointF(x, y)

if __name__ == "__main__":
    app = QApplication([])
    house = BigBrotherHouse()
    house.show()
    app.exec_()
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt5.QtGui import QBrush, QPen, QColor, QFont
import random


class HouseGuestItem(QGraphicsItem):
    def __init__(self, initials, position, color, parent=None):
        super().__init__(parent)
        self.initials = initials
        self.color = color
        self.setPos(position)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)

    def boundingRect(self):
        return QRectF(-12, -12, 24, 24)  # Reduce the bounding rect size

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))  # Reduce the pen width
        painter.drawEllipse(-12, -12, 24, 24)  # Reduce the ellipse size
        font = QFont()
        font.setPointSize(8)  # Reduce the font size
        painter.setFont(font)
        painter.drawText(QRectF(-12, -12, 24, 24), Qt.AlignCenter, self.initials)


class BigBrotherHouse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Big Brother House")
        self.setGeometry(100, 100, 1000, 800)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.grid_size = 50
        self.create_house()

    def create_next_element(self):
        if self.creation_step < len(self.rooms):
            self.scene.addItem(self.rooms[self.creation_step])
            self.scene.addItem(self.labels[self.creation_step])
            self.creation_step += 1
        elif self.creation_step < len(self.rooms) + len(self.hallways):
            self.scene.addItem(self.hallways[self.creation_step - len(self.rooms)])
            self.creation_step += 1
        elif self.creation_step < len(self.rooms) + len(self.hallways) + len(
            self.doors
        ):
            self.scene.addItem(
                self.doors[self.creation_step - len(self.rooms) - len(self.hallways)]
            )
            self.creation_step += 1
        else:
            self.timer.stop()
            self.add_houseguests()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.move_houseguests)
            self.timer.start(100)  # Move houseguests every 1 second

    def create_house(self):
        house_width = self.width() - 20
        house_height = self.height() - 20
        num_cols = house_width // self.grid_size
        num_rows = house_height // self.grid_size

        self.grid = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
        self.rooms = []
        self.hallways = []
        self.doors = []
        self.labels = []

        room_presets = [
            (4, 4),  # Small room (4x4 cells)
            (6, 4),  # Medium room (6x4 cells)
            (6, 6),  # Large room (6x6 cells)
            (8, 8),  # XL room (8x8 cells)
        ]

        # 1. Create and label the rooms
        num_rooms = random.randint(10, 20)
        for i in range(num_rooms):
            preset = random.choice(room_presets)
            room_cols, room_rows = preset

            found_space = False
            max_attempts = 100
            attempts = 0
            while not found_space and attempts < max_attempts:
                col = random.randint(0, num_cols - room_cols)
                row = random.randint(0, num_rows - room_rows)
                if all(
                    self.grid[r][c] == 0
                    for r in range(row, row + room_rows)
                    for c in range(col, col + room_cols)
                ):
                    for r in range(row, row + room_rows):
                        for c in range(col, col + room_cols):
                            self.grid[r][c] = 1
                    found_space = True
                else:
                    attempts += 1

            if found_space:
                room_x = col * self.grid_size + 10
                room_y = row * self.grid_size + 10
                room_width = room_cols * self.grid_size
                room_height = room_rows * self.grid_size
                room = QGraphicsRectItem(room_x, room_y, room_width, room_height)
                room.setBrush(QBrush(Qt.gray))
                room.setPen(QPen(Qt.black, 4))
                self.rooms.append(room)
                # Remove the line that adds the room to the scene
                # self.scene.addItem(room)

                # Add room label
                label_text = f"Room {i+1}"
                label = QGraphicsTextItem(label_text)
                label.setPos(room_x + 5, room_y + 5)
                label.setFont(QFont("Arial", 10))
                self.labels.append(label)
                # Remove the line that adds the label to the scene
                # self.scene.addItem(label)

        # Connect adjacent rooms with doors
        # Connect adjacent rooms with doors
        for i in range(len(self.rooms)):
            room = self.rooms[i]

            for j in range(i + 1, len(self.rooms)):
                other_room = self.rooms[j]

                # Check if the rooms are truly adjacent (share a side and are within one grid size)
                is_adjacent = False
                if (
                    abs(room.rect().right() - other_room.rect().left())
                    <= self.grid_size
                    and abs(room.rect().top() - other_room.rect().top())
                    <= self.grid_size
                ):
                    is_adjacent = True
                elif (
                    abs(room.rect().left() - other_room.rect().right())
                    <= self.grid_size
                    and abs(room.rect().top() - other_room.rect().top())
                    <= self.grid_size
                ):
                    is_adjacent = True
                elif (
                    abs(room.rect().bottom() - other_room.rect().top())
                    <= self.grid_size
                    and abs(room.rect().left() - other_room.rect().left())
                    <= self.grid_size
                ):
                    is_adjacent = True
                elif (
                    abs(room.rect().top() - other_room.rect().bottom())
                    <= self.grid_size
                    and abs(room.rect().left() - other_room.rect().left())
                    <= self.grid_size
                ):
                    is_adjacent = True

                if is_adjacent:
                    # Determine the side where the door should be placed
                    if (
                        abs(room.rect().right() - other_room.rect().left())
                        <= self.grid_size
                    ):
                        # Place door on the shared vertical side
                        door_x = int(room.rect().right() - self.grid_size // 2)
                        door_y = (
                            int(min(room.rect().top(), other_room.rect().top()))
                            + self.grid_size // 10
                        )
                        door_width = self.grid_size
                        door_height = self.grid_size - 2 * (self.grid_size // 10)

                    elif (
                        abs(room.rect().left() - other_room.rect().right())
                        <= self.grid_size
                    ):
                        # Place door on the shared vertical side
                        door_x = int(room.rect().left() - self.grid_size // 2)
                        door_y = (
                            int(min(room.rect().top(), other_room.rect().top()))
                            + self.grid_size // 10
                        )
                        door_width = self.grid_size
                        door_height = self.grid_size - 2 * (self.grid_size // 10)

                    elif (
                        abs(room.rect().bottom() - other_room.rect().top())
                        <= self.grid_size
                    ):
                        # Place door on the shared horizontal side
                        door_x = (
                            int(min(room.rect().left(), other_room.rect().left()))
                            + self.grid_size // 10
                        )
                        door_y = int(room.rect().bottom() - self.grid_size // 2)
                        door_width = self.grid_size - 2 * (self.grid_size // 10)
                        door_height = self.grid_size

                    else:
                        # Place door on the shared horizontal side
                        door_x = (
                            int(min(room.rect().left(), other_room.rect().left()))
                            + self.grid_size // 10
                        )
                        door_y = int(room.rect().top() - self.grid_size // 2)
                        door_width = self.grid_size - 2 * (self.grid_size // 10)
                        door_height = self.grid_size

                    # Create the door
                    door = QGraphicsRectItem(door_x, door_y, door_width, door_height)
                    door.setBrush(QBrush(Qt.darkGreen))
                    # self.scene.addItem(door)
                    self.doors.append(door)

        # Draw grid lines
        for x in range(0, house_width, self.grid_size):
            self.scene.addItem(QGraphicsLineItem(x + 10, 10, x + 10, house_height - 10))
        for y in range(0, house_height, self.grid_size):
            self.scene.addItem(QGraphicsLineItem(10, y + 10, house_width - 10, y + 10))

        self.creation_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.create_next_element)
        self.timer.start(100)  # Delay of 1 second between each element

    def connect_rooms_vertically(self, room, other_room):
        hallway_x = int(room.rect().right())
        hallway_y = int(max(room.rect().top(), other_room.rect().top()))
        hallway_width = self.grid_size
        hallway_height = int(
            min(room.rect().bottom(), other_room.rect().bottom()) - hallway_y
        )

        # Check if the hallway overlaps with any existing rooms
        hallway_col = (hallway_x - 10) // self.grid_size
        hallway_row = (hallway_y - 10) // self.grid_size
        if all(
            self.grid[hallway_row + r][hallway_col] == 0
            for r in range(hallway_height // self.grid_size)
        ):
            hallway = QGraphicsRectItem(
                hallway_x, hallway_y, hallway_width, hallway_height
            )
            hallway.setBrush(QBrush(Qt.lightGray))
            self.hallways.append(hallway)
            self.scene.addItem(hallway)

            # Add door at the end of the hallway
            door_y = hallway_y + (hallway_height - self.grid_size) // 2
            door = QGraphicsRectItem(hallway_x - 5, door_y, 10, self.grid_size)
            door.setBrush(QBrush(Qt.darkGreen))
            self.scene.addItem(door)
            self.doors.append(door)

    def connect_rooms_horizontally(self, room, other_room):
        hallway_x = int(max(room.rect().left(), other_room.rect().left()))
        hallway_y = int(room.rect().bottom())
        hallway_width = int(
            min(room.rect().right(), other_room.rect().right()) - hallway_x
        )
        hallway_height = self.grid_size

        # Check if the hallway overlaps with any existing rooms
        hallway_col = (hallway_x - 10) // self.grid_size
        hallway_row = (hallway_y - 10) // self.grid_size
        if all(
            self.grid[hallway_row][hallway_col + c] == 0
            for c in range(hallway_width // self.grid_size)
        ):
            hallway = QGraphicsRectItem(
                hallway_x, hallway_y, hallway_width, hallway_height
            )
            hallway.setBrush(QBrush(Qt.lightGray))
            self.hallways.append(hallway)
            self.scene.addItem(hallway)

            # Add door at the end of the hallway
            door_x = hallway_x + (hallway_width - self.grid_size) // 2
            door = QGraphicsRectItem(door_x, hallway_y - 5, self.grid_size, 10)
            door.setBrush(QBrush(Qt.darkGreen))
            self.scene.addItem(door)
            self.doors.append(door)

    def connect_rooms(self):
        self.doors = []
        for i in range(len(self.rooms)):
            room = self.rooms[i]
            for j in range(i + 1, len(self.rooms)):
                other_room = self.rooms[j]

                if abs(room.rect().left() - other_room.rect().right()) < 10:
                    # Connect rooms with a vertical hallway
                    hallway_x = room.rect().right()
                    hallway_y = max(room.rect().top(), other_room.rect().top())
                    hallway_width = 10
                    hallway_height = (
                        min(room.rect().bottom(), other_room.rect().bottom())
                        - hallway_y
                    )
                    hallway = QGraphicsRectItem(
                        hallway_x, hallway_y, hallway_width, hallway_height
                    )
                    hallway.setBrush(QBrush(Qt.lightGray))
                    self.scene.addItem(hallway)

                    # Add doors at the ends of the hallway
                    door1_x = hallway_x - 5
                    door1_y = hallway_y
                    door2_x = hallway_x - 5
                    door2_y = hallway_y + hallway_height - 10
                    door1 = QGraphicsRectItem(door1_x, door1_y, 10, 10)
                    door2 = QGraphicsRectItem(door2_x, door2_y, 10, 10)
                    door1.setBrush(QBrush(Qt.darkGreen))
                    door2.setBrush(QBrush(Qt.darkGreen))
                    self.scene.addItem(door1)
                    self.scene.addItem(door2)
                    self.doors.extend([door1, door2])
                elif abs(room.rect().top() - other_room.rect().bottom()) < 10:
                    # Connect rooms with a horizontal hallway
                    hallway_x = max(room.rect().left(), other_room.rect().left())
                    hallway_y = room.rect().bottom()
                    hallway_width = (
                        min(room.rect().right(), other_room.rect().right()) - hallway_x
                    )
                    hallway_height = 10
                    hallway = QGraphicsRectItem(
                        hallway_x, hallway_y, hallway_width, hallway_height
                    )
                    hallway.setBrush(QBrush(Qt.lightGray))
                    self.scene.addItem(hallway)

                    # Add doors at the ends of the hallway
                    door1_x = hallway_x
                    door1_y = hallway_y - 5
                    door2_x = hallway_x + hallway_width - 10
                    door2_y = hallway_y - 5
                    door1 = QGraphicsRectItem(door1_x, door1_y, 10, 10)
                    door2 = QGraphicsRectItem(door2_x, door2_y, 10, 10)
                    door1.setBrush(QBrush(Qt.darkGreen))
                    door2.setBrush(QBrush(Qt.darkGreen))
                    self.scene.addItem(door1)
                    self.scene.addItem(door2)
                    self.doors.extend([door1, door2])

    def add_houseguests(self):
        self.houseguests = []
        colors = [
            Qt.red,
            Qt.green,
            Qt.blue,
            Qt.yellow,
            Qt.cyan,
            Qt.magenta,
            Qt.darkYellow,
        ]
        num_hg = 7
        spawns = []
        for x in range(num_hg):
            pos = self.get_random_position_in_room(
                self.rooms[random.randint(0, len(self.rooms) - 1)]
            )
            if pos not in spawns:
                spawns.append(pos)
                initials = f"{chr(65 + x)}{chr(65 + x)}"
                color = self.get_unique_color()
                self.houseguests.append(HouseGuestItem(initials, pos, color))
                self.scene.addItem(self.houseguests[-1])

    def move_houseguests(self):
        for hg in self.houseguests:
            current_pos = hg.pos()
            current_row = int(
                (current_pos.y() - 10 - self.grid_size // 2) // self.grid_size
            )
            current_col = int(
                (current_pos.x() - 10 - self.grid_size // 2) // self.grid_size
            )

            if 0 <= current_row < len(self.grid) and 0 <= current_col < len(
                self.grid[0]
            ):
                if self.grid[current_row][current_col] == 1 or any(
                    door.contains(current_pos) for door in self.doors
                ):
                    adjacent_positions = []
                    for row, col in [
                        (current_row - 1, current_col),
                        (current_row + 1, current_col),
                        (current_row, current_col - 1),
                        (current_row, current_col + 1),
                    ]:
                        if (
                            0 <= row < len(self.grid)
                            and 0 <= col < len(self.grid[0])
                            and (
                                self.grid[row][col] == 1
                                or any(
                                    door.contains(
                                        QPointF(
                                            col * self.grid_size
                                            + self.grid_size // 2
                                            + 10,
                                            row * self.grid_size
                                            + self.grid_size // 2
                                            + 10,
                                        )
                                    )
                                    for door in self.doors
                                )
                            )
                        ):
                            new_pos = QPointF(
                                col * self.grid_size + self.grid_size // 2 + 10,
                                row * self.grid_size + self.grid_size // 2 + 10,
                            )
                            if not any(hg.pos() == new_pos for hg in self.houseguests):
                                adjacent_positions.append(new_pos)

                    if adjacent_positions:
                        new_pos = random.choice(adjacent_positions)
                        hg.setPos(new_pos)
                    else:
                        hg.setPos(current_pos)
                else:
                    valid_positions = []
                    for room in self.rooms:
                        valid_positions.extend(
                            [self.get_random_position_in_room(room) for _ in range(10)]
                        )
                    if valid_positions:
                        new_pos = random.choice(valid_positions)
                        hg.setPos(new_pos)
            else:
                valid_positions = []
                for room in self.rooms:
                    valid_positions.extend(
                        [self.get_random_position_in_room(room) for _ in range(10)]
                    )
                if valid_positions:
                    new_pos = random.choice(valid_positions)
                    hg.setPos(new_pos)

    def get_random_position_in_room(self, room):
        col = random.randint(0, int(room.rect().width() - 24) // self.grid_size)
        row = random.randint(0, int(room.rect().height() - 24) // self.grid_size)
        x = room.rect().x() + col * self.grid_size + self.grid_size // 2
        y = room.rect().y() + row * self.grid_size + self.grid_size // 2
        return QPointF(x, y)

    def get_unique_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return QColor(r, g, b)


if __name__ == "__main__":
    app = QApplication([])
    house = BigBrotherHouse()
    house.show()
    app.exec_()

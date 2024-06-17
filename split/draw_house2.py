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
        return QRectF(-12, -12, 24, 24)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(-12, -12, 24, 24)
        font = QFont()
        font.setPointSize(8)
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

    def create_house(self):
        house_width = self.width() - 20
        house_height = self.height() - 20
        num_cols = house_width // self.grid_size
        num_rows = house_height // self.grid_size

        self.grid = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
        self.rooms = []
        self.doors = []
        self.labels = []

        room_presets = [
            (4, 4),  # Small room (4x4 cells)
            (6, 4),  # Medium room (6x4 cells)
            (6, 6),  # Large room (6x6 cells)
            (8, 8),  # XL room (8x8 cells)
        ]

        # Create and label the rooms
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
                self.scene.addItem(room)

                # Add room label
                label_text = f"Room {i+1}"
                label = QGraphicsTextItem(label_text)
                label.setPos(room_x + 5, room_y + 5)
                label.setFont(QFont("Arial", 10))
                self.labels.append(label)
                self.scene.addItem(label)

        # Connect adjacent rooms with doors
        for i in range(len(self.rooms)):
            room = self.rooms[i]
            for j in range(i + 1, len(self.rooms)):
                other_room = self.rooms[j]

                if (
                    room.rect().right() == other_room.rect().left()
                    or room.rect().left() == other_room.rect().right()
                ):
                    # Vertical door
                    door_x = int(max(room.rect().left(), other_room.rect().left()))
                    door_y = int(
                        min(room.rect().top(), other_room.rect().top())
                        + (
                            max(room.rect().bottom(), other_room.rect().bottom())
                            - min(room.rect().top(), other_room.rect().top())
                        )
                        // 2
                        - self.grid_size // 4
                    )
                    door_width = self.grid_size // 2
                    door_height = self.grid_size // 2
                elif (
                    room.rect().bottom() == other_room.rect().top()
                    or room.rect().top() == other_room.rect().bottom()
                ):
                    # Horizontal door
                    door_x = int(
                        min(room.rect().left(), other_room.rect().left())
                        + (
                            max(room.rect().right(), other_room.rect().right())
                            - min(room.rect().left(), other_room.rect().left())
                        )
                        // 2
                        - self.grid_size // 4
                    )
                    door_y = int(max(room.rect().top(), other_room.rect().top()))
                    door_width = self.grid_size // 2
                    door_height = self.grid_size // 2
                else:
                    continue

                door = QGraphicsRectItem(door_x, door_y, door_width, door_height)
                door.setBrush(QBrush(Qt.darkGreen))
                self.doors.append(door)
                self.scene.addItem(door)

        self.add_houseguests()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_houseguests)
        self.timer.start(100)

    def add_houseguests(self):
        self.houseguests = []
        num_hg = 7
        for _ in range(num_hg):
            room = random.choice(self.rooms)
            pos = self.get_random_position_in_room(room)
            initials = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
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
                    room = random.choice(self.rooms)
                    new_pos = self.get_random_position_in_room(room)
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
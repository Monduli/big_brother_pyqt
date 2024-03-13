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
        # Create the house layout using QGraphicsRectItem
        self.rooms = [
            QGraphicsRectItem(100, 100, 200, 200),  # Living Room
            QGraphicsRectItem(400, 100, 200, 200),  # Kitchen
            QGraphicsRectItem(700, 100, 200, 200),  # Bedroom 1
            QGraphicsRectItem(100, 400, 200, 200),  # Bedroom 2
            QGraphicsRectItem(400, 400, 200, 200),  # Bedroom 3
            QGraphicsRectItem(700, 400, 200, 200),  # Bedroom 4
            QGraphicsRectItem(100, 600, 200, 100),  # Bathroom
            QGraphicsRectItem(400, 600, 500, 100)  # Backyard
        ]

        # Add walls and hallways to the house
        wall1 = QGraphicsRectItem(0, 0, 1000, 100)  # Top wall
        wall2 = QGraphicsRectItem(0, 700, 1000, 100)  # Bottom wall
        wall3 = QGraphicsRectItem(0, 100, 100, 600)  # Left wall
        wall4 = QGraphicsRectItem(900, 100, 100, 600)  # Right wall
        hallway1 = QGraphicsRectItem(300, 200, 400, 100)  # Horizontal hallway
        hallway2 = QGraphicsRectItem(600, 300, 100, 200)  # Vertical hallway

        for room in self.rooms:
            room.setBrush(QBrush(Qt.gray))
            room.setPen(QPen(Qt.black, 2))
            self.scene.addItem(room)

        for wall in [wall1, wall2, wall3, wall4]:
            wall.setBrush(QBrush(Qt.darkGray))
            wall.setPen(QPen(Qt.black, 2))
            self.scene.addItem(wall)

        for hallway in [hallway1, hallway2]:
            hallway.setBrush(QBrush(Qt.lightGray))
            hallway.setPen(QPen(Qt.black, 2))
            self.scene.addItem(hallway)

    def add_houseguests(self):
        # Define a list of colors for the houseguests
        colors = [Qt.red, Qt.green, Qt.blue, Qt.yellow, Qt.cyan, Qt.magenta, Qt.darkYellow]

        # Add houseguests to the scene
        self.houseguests = [
            HouseGuestItem("AA", QPointF(150, 150), colors[0]),
            HouseGuestItem("BB", QPointF(450, 150), colors[1]),
            HouseGuestItem("CC", QPointF(750, 150), colors[2]),
            HouseGuestItem("DD", QPointF(150, 450), colors[3]),
            HouseGuestItem("EE", QPointF(450, 450), colors[4]),
            HouseGuestItem("FF", QPointF(750, 450), colors[5]),
            HouseGuestItem("GG", QPointF(150, 650), colors[6])
        ]

        for hg in self.houseguests:
            self.scene.addItem(hg)

    def move_houseguests(self):
        for hg in self.houseguests:
            current_room = self.get_room_for_position(hg.pos())
            adjacent_rooms = self.get_adjacent_rooms(current_room)
            if adjacent_rooms:
                new_room = random.choice(adjacent_rooms)
                new_pos = self.get_random_position_in_room(new_room)
                hg.setPos(new_pos)

    def get_room_for_position(self, position):
        for room in self.rooms:
            if room.contains(position):
                return room
        return None

    def get_adjacent_rooms(self, room):
        adjacent_rooms = []
        for other_room in self.rooms:
            if other_room != room and room.collidesWithItem(other_room):
                adjacent_rooms.append(other_room)
        return adjacent_rooms

    def are_rooms_adjacent(self, room1, room2):
        # Check if the rooms share a common wall or are connected by a hallway
        x1, y1, w1, h1 = room1.rect().getCoords()
        x2, y2, w2, h2 = room2.rect().getCoords()

        # Check if the rooms share a vertical wall
        if (
            (x1 == x2 + w2 or x2 == x1 + w1) and
            y1 <= y2 + h2 and y1 + h1 >= y2
        ):
            return True

        # Check if the rooms share a horizontal wall
        elif (
            (y1 == y2 + h2 or y2 == y1 + h1) and
            x1 <= x2 + w2 and x1 + w1 >= x2
        ):
            return True

        # Check if the rooms are connected by a hallway
        else:
            for hallway in [h for h in self.rooms if h.rect().width() < h.rect().height()]:
                hx, hy, hw, hh = hallway.rect().getCoords()
                if (
                    (hx == x1 + w1 and hy == y1) or
                    (hx == x2 + w2 and hy == y2) or
                    (hy == y1 + h1 and hx == x1) or
                    (hy == y2 + h2 and hx == x2)
                ):
                    return True

        return False

    def get_random_position_in_room(self, room):
        x = random.uniform(room.rect().x() + 25, room.rect().x() + room.rect().width() - 25)
        y = random.uniform(room.rect().y() + 25, room.rect().y() + room.rect().height() - 25)
        return QPointF(x, y)

if __name__ == "__main__":
    app = QApplication([])
    house = BigBrotherHouse()
    house.show()
    app.exec_()
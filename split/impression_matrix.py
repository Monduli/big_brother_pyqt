from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QLabel, QPushButton, QVBoxLayout,
                             QWidget)


class ColoredLabel(QLabel):
    def __init__(self, value, parent=None):
        super().__init__(parent)
        self.value = value
        self.update_color()

    def update_color(self):
        color = "#FFFFFF" # default color
        if self.value == "X":
            self.setStyleSheet("background-color: gray; color: white;")
        else:
            value = int(self.value)
            if value == 1:
                color = "#D10A0A"
            elif value == 2:
                color = "#fe5f00"
            elif value == 3:
                color = "#fe8b00"
            elif value == 4: 
                color = "#ffb000"
            elif value == 5: 
                color = "#fcd303"
            elif value == 6: 
                color = "#cfcd00"
            elif value == 7: 
                color = "#a2c600"
            elif value == 8:
                color = "#70bd00"
            elif value == 9:
                color = "#30b200"
            elif value == 10:
                color = "#45FF00"
            self.setStyleSheet(f"background-color: {color}; color: black;") 

    def setValue(self, value):
        self.value = value
        self.update_color()
        self.setText(str(value))

class ImpressionMatrix(QWidget):
    def __init__(self, houseguests):
        super().__init__()
        self.houseguests = houseguests
        self.impressions = {}
        for hg in houseguests:
            self.impressions[hg.name] = hg.impressions.copy()
        self.show_values = True
        self.init_matrix()
        self.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
            }
            """
        )

        # Create layout and add matrix and button
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.grid)
        self.setLayout(main_layout)

    def init_matrix(self):
        # Create grid layout
        self.grid = QGridLayout()

        # Size the grid based on number of houseguests
        num_hgs = len(self.houseguests)
        self.grid.setColumnStretch(0, 1)
        self.grid.setRowStretch(0, 1)
        self.grid.setColumnMinimumWidth(0, 75)
        self.grid.setRowMinimumHeight(0, 75)
        for col in range(1, num_hgs + 1):
            self.grid.setColumnStretch(col, 1)
            self.grid.setColumnMinimumWidth(col, 75)
        for row in range(1, num_hgs + 1):
            self.grid.setRowStretch(row, 1)
            self.grid.setRowMinimumHeight(row, 75)

        # Add names along top row and left column
        for col, hg in enumerate(self.houseguests):
            name = QLabel(hg.name)
            name.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(name, 0, col + 1)

        for row, hg in enumerate(self.houseguests):
            name = QLabel(hg.name)
            name.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(name, row + 1, 0)
            
        for row, hg1 in enumerate(self.houseguests):
            for col, hg2 in enumerate(self.houseguests):
                if hg1 != hg2:
                    label = ColoredLabel(self.impressions[hg1.name][hg2.name])  
                else:
                    label = ColoredLabel("X")
                label.setAlignment(Qt.AlignCenter)
                self.grid.addWidget(label, row + 1, col + 1)  

        # Add impression values to grid
        self.update_matrix()

    def update_matrix(self):
        for row, hg1 in enumerate(self.houseguests):
            for col, hg2 in enumerate(self.houseguests):
                if hg1 != hg2:
                    value = self.impressions[hg1.name][hg2.name]
                    if self.show_values:
                        label = QLabel(str(value))
                    else:
                        label = ColoredLabel(value) 
                else:
                    label = ColoredLabel("X")
                label.setAlignment(Qt.AlignCenter)
                self.grid.addWidget(label, row + 1, col + 1) 

    def appear(self, houseguests):
        self.impressions = {}
        for hg in houseguests:
            self.impressions[hg.name] = hg.impressions.copy()
        self.init_matrix()
        self.show()
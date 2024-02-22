from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget


class ImpressionMatrix(QWidget):
    def __init__(self, houseguests):
        super().__init__()
        self.houseguests = houseguests
        self.impressions = {}
        for hg in houseguests:
            self.impressions[hg.name] = hg.impressions.copy()
        print(self.impressions)
        self.init_matrix()
        self.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
            }
            """
        )

    def init_matrix(self):
        # Create grid layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Size the grid based on number of houseguests
        num_hgs = len(self.houseguests)
        grid.setColumnStretch(0, 1)
        grid.setRowStretch(0, 1)
        grid.setColumnMinimumWidth(0, 75)
        grid.setRowMinimumHeight(0, 75)
        for col in range(1, num_hgs + 1):
            grid.setColumnStretch(col, 1)
            grid.setColumnMinimumWidth(col, 75)
        for row in range(1, num_hgs + 1):
            grid.setRowStretch(row, 1)
            grid.setRowMinimumHeight(row, 75)

        # Add names along top row and left column
        for col, hg in enumerate(self.houseguests):
            name = QLabel(hg.name)
            name.setAlignment(Qt.AlignCenter)
            grid.addWidget(name, 0, col + 1)

        for row, hg in enumerate(self.houseguests):
            name = QLabel(hg.name)
            name.setAlignment(Qt.AlignCenter)
            grid.addWidget(name, row + 1, 0)

        # Add impression values to grid
        for row, hg1 in enumerate(self.houseguests):
            for col, hg2 in enumerate(self.houseguests):
                if hg1 != hg2:
                    print(hg1.name, hg2.name)
                    value = QLabel(str(self.impressions[hg1.name][hg2.name]))
                else:
                    value = QLabel(str("X"))
                value.setAlignment(Qt.AlignCenter)
                grid.addWidget(value, row + 1, col + 1)

    def appear(self, houseguests):
        self.impressions = {}
        for hg in houseguests:
            self.impressions[hg.name] = hg.impressions.copy()
        # print(self.impressions)
        self.init_matrix()
        self.show()

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from constants import *

from game import BigBrother as bb
from game_v1 import BigBrother as bb1
from game_v2 import BigBrother as bb2

VERSION = 1  # Set the default version here


class LegendsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Legends Mode")

        # Create the main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Add the legends selection section
        self.legends_selection_layout = QHBoxLayout()
        self.legends_label = QLabel("Choose Season:")
        self.legends_combobox = QComboBox()
        for season_key in legends_data:
            if season_key.startswith("US"):
                season_num = int(season_key[2:])
                self.legends_combobox.addItem(f"US Season {season_num}")
            elif season_key.startswith("CA"):
                season_num = int(season_key[2:])
                self.legends_combobox.addItem(f"Canada Season {season_num}")
        self.legends_selection_layout.addWidget(self.legends_label)
        self.legends_selection_layout.addWidget(self.legends_combobox)
        main_layout.addLayout(self.legends_selection_layout)

        # Add the start button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_legends_mode)
        main_layout.addWidget(self.start_button)

        # Add the back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.close)
        main_layout.addWidget(self.back_button)

        self.setCentralWidget(central_widget)

    def start_legends_mode(self):
        # Get the selected season from the combobox
        selected_season_index = self.legends_combobox.currentIndex()
        season_keys = list(legends_data.keys())
        selected_season_key = season_keys[selected_season_index]

        # Close the Legends Mode window
        self.close()

        # Launch the game with the selected season
        launch_game(season=selected_season_key)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Big Brother Simulator")

        # Create the main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Add the mode selection section
        mode_selection_layout = QHBoxLayout()
        self.random_mode_button = QPushButton("Random Mode")
        self.random_mode_button.clicked.connect(self.start_random_mode)
        self.legends_mode_button = QPushButton("Legends Mode")
        self.legends_mode_button.clicked.connect(self.start_legends_mode)
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        mode_selection_layout.addWidget(self.random_mode_button)
        mode_selection_layout.addWidget(self.legends_mode_button)
        mode_selection_layout.addWidget(self.quit_button)
        main_layout.addLayout(mode_selection_layout)

        self.setCentralWidget(central_widget)

    def start_random_mode(self):
        self.close()
        launch_game()

    def start_legends_mode(self):
        legends_window = LegendsWindow(self)
        legends_window.show()


def launch_game(pre=None, season=None):
    """
    Launches the Big Brother game simulation based on the specified version.

    The version is determined by the value of the VERSION constant.
    - If VERSION is 1, an instance of the BigBrother class from the game module is created.
    - If VERSION is 2, an instance of the BigBrother class from the game_v1 module is created.
    - If VERSION is 3, an instance of the BigBrother class from the game_v2 module is created.

    Returns:
        None
    """
    if VERSION == 1:
        game_instance = bb(
            season
        )  # Create an instance of the BigBrother class from game module
    elif VERSION == 2:
        game_instance = bb1(
            season
        )  # Create an instance of the BigBrother class from game_v1 module
    elif VERSION == 3:
        game_instance = bb2(
            season
        )  # Create an instance of the BigBrother class from game_v2 module


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(14)
    app.setFont(font)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

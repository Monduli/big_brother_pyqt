import random
import re
import sys
from copy import deepcopy

import names
from alliance import Alliance
from bberror import BBError
from constants import *
from customtextedit import CustomTextEdit
from events import Events
from houseguest import HouseGuest
from impression_matrix import ImpressionMatrix
from name_edit import EditNameDialog
from PyQt5.QtCore import QSettings, Qt, QTimer
from PyQt5.QtGui import QColor, QPalette, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QColorDialog,
                             QComboBox, QDialog, QDialogButtonBox,
                             QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem, QMenuBar,
                             QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
                             QStyle, QStyledItemDelegate, QTextEdit,
                             QVBoxLayout, QWidget)
from utils import Utility


class BigBrother(QWidget):

    def __init__(self):
        super().__init__()
        self.num_players = NUM_PLAYERS
        self.houseguests = []
        self.evicted_houseguests = []
        self.HOH = None
        self.nominees = []
        self.veto_winner = None
        self.evicted = None
        self.prev_HOH = None
        self.used = None
        self.end_state = 0
        self.events = []  # Initialize a list to store events
        self.alliances = {}  # Initialize a dictionary to store alliances
        self.settings = QSettings("Danco", "BBQT")
        self.num_players = NUM_PLAYERS
        self.print_speed = 0.8
        self.season_num = 1
        self.chosen_hg = None
        self.clicked_hg = None
        self.week = 0
        self.noms_for_list = None
        self.renoms_for_list = None
        self.debug_mode = self.settings.value("DebugMode", False, type=bool)
        self.debug_impressions = True
        self.step_index = 0
        self.formatting = {}
        self.create_players()
        self.do_impressions()
        self.initUI()
        self.utility = Utility(self)
        self.events = Events(self)
        self.showmances = []
        self.introduce_players()

    def initUI(self):
        # Create the QListWidget and add all houseguests
        self.setMinimumSize(1200, 800)

        # Colors
        self.chosen_color = QColor(220, 220, 220)
        self.hoh_color = QColor("#FFFF00")  # Yellow
        self.noms_color = QColor("#6A5ACD")  # Slate Blue
        self.veto_color = QColor("#FFA500")  # Orange
        self.replacement_noms_color = QColor("#1A1ABB")  #
        self.evicted_color = QColor("#FFEBEB")  # Purple
        self.no_color = QColor("#FFFFFF")
        self.imp_color = QColor("#FA00B3")
        self.name_color = QColor("#00FF00")
        self.evict_statement_color = QColor("#FF0000") # Red
        self.list_items = []
        self.houseguest_list_widget = QListWidget()
        for hg in self.houseguests:
            self.houseguest_list_widget.addItem(hg.name)
            self.list_items.append(hg.name)
        self.houseguest_list_widget.itemDoubleClicked.connect(self.edit_hg_name)
        self.houseguest_list_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.retain_season = self.settings.value("RetainSeason", defaultValue=False)

        # Set layout
        overall = QVBoxLayout()
        layout = QHBoxLayout()

        # Create widget for left side
        self.left_widget = QWidget()

        # Layout for labels on left
        self.left_layout = QVBoxLayout()

        self.title_season_label = QLabel("Big Brother (US)")

        # Create list widget for left side information
        self.left_list_widget = QListWidget()
        self.left_list_widget.setStyleSheet("QListWidget::item { padding: 5px; }")
        self.left_list_widget.setItemDelegate(NoFocusDelegate())
        self.left_list_widget.setWordWrap(True)

        # Create bold font for category titles
        bold_font = self.left_list_widget.font()
        bold_font.setBold(True)

        # Add title item
        title_item = QListWidgetItem("Big Brother (US)")
        title_item.setFont(bold_font)
        self.left_list_widget.addItem(title_item)

        # Layout for left widget
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.title_season_label)
        self.left_layout.addWidget(self.left_list_widget)

        # Then add the widget to the main layout
        # layout.addWidget(self.left_widget)

        # Create menu bar
        menu_bar = QMenuBar()
        screen = QApplication.primaryScreen()
        menu_bar.setMinimumWidth(screen.size().width())  # Set minimum width to 600px
        menu_bar.setMaximumHeight(28)
        menu_bar.setContentsMargins(20, 0, 20, 0)  # Left/right margins of 20px
        layout.setMenuBar(menu_bar)

        layout.setContentsMargins(0, 30, 0, 0)

        # Create File menu
        file_menu = menu_bar.addMenu("Options")

        # Add Reset, Preferences, and Exit actions to File menu
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset)
        file_menu.addAction(reset_action)

        preferences_action = QAction("Preferences...", self)
        preferences_action.triggered.connect(
            self.show_preferences
        )  # Implement this method
        file_menu.addAction(preferences_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Allow clicking a houseguest to choose them
        self.houseguest_list_widget.itemClicked.connect(self.store_clicked_hg)
        self.choose_hg_btn = QPushButton("Follow HouseGuest")
        self.choose_hg_btn.clicked.connect(self.choose_houseguest)

        # self.choose_color_btn = QPushButton("Choose Color")
        # self.choose_color_btn.clicked.connect(choose_color)

        self.play_continuously_btn = QPushButton("Play Continuously (Debug)")
        self.play_continuously_btn.clicked.connect(self.play_continuously)

        # Add "Impressions" button
        self.impressions_btn = QPushButton("Impressions")
        self.impressions_btn.clicked.connect(self.show_impressions)

        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.houseguest_list_widget)
        middle_layout.addWidget(self.choose_hg_btn)
        self.houseguest_list_widget.setProperty("verticalAlignment", "AlignTop")
        self.choose_hg_btn.setProperty("verticalAlignment", "AlignBottom")

        # Set the layout on the widget
        self.left_widget.setLayout(self.left_layout)

        # Then add the widget to the main layout
        layout.addWidget(self.left_widget, stretch=1)

        self.proceed_btn = QPushButton("Proceed")
        self.proceed_btn.clicked.connect(self.proceed)

        # Add Continue button
        self.next_week_btn = QPushButton("Forward 1 Week")
        self.next_week_btn.clicked.connect(self.play_week)

        # Add reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)
        
        # Add "Showmances" button
        self.showmances_btn = QPushButton("Showmances")
        self.showmances_btn.clicked.connect(self.show_showmances)

        # Add "Alliances" button
        self.alliances_btn = QPushButton("Alliances")
        self.alliances_btn.clicked.connect(self.show_alliances)
        
        top_buttons = QHBoxLayout()
        
        top_buttons.addWidget(self.showmances_btn)
        top_buttons.addWidget(self.alliances_btn)
        top_buttons.addWidget(self.impressions_btn)

        button_layout = QVBoxLayout()
        button_layout.addLayout(top_buttons)
        button_layout.addWidget(self.proceed_btn)
        button_layout.addWidget(self.next_week_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.play_continuously_btn)
        
        # Add the buttons to the layout
        

        # Add text display box
        self.text_box = CustomTextEdit()
        self.text_box.setReadOnly(True)

        layout.addLayout(middle_layout, stretch=1)

        layout.addWidget(self.text_box, stretch=1)

        overall.addLayout(layout)
        overall.addLayout(button_layout)

        self.setLayout(overall)

        self.dark_style_sheet("self")

        dark_palette = self.make_dark_palette()

        self.setPalette(dark_palette)
        self.show()

    def store_clicked_hg(self, item):
        self.clicked_hg = item.text()

    def set_chosen_houseguest(self):
        hg = next(h for h in self.houseguests if h.name == self.clicked_hg)
        item = self.houseguest_list_widget.findItems(self.clicked_hg, Qt.MatchExactly)[
            0
        ]

        item.setBackground(QColor(255, 255, 0))
        item.setFont(item.font())

        self.choose_hg_btn.setDisabled(True)
        self.houseguest_list_widget.itemClicked.disconnect()

        # Set the chosen houseguest
        self.chosen_hg = hg

    def dark_style_sheet(self, target):
        if target == "self":
            self.setStyleSheet(
                """
                QLabel, QCheckBox {
                    font-size: 20px;
                    color: white; 
                }
                QPushButton {
                    background-color: #2D2D2D;
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #3D3D3D;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
                QTextEdit, QListWidget {
                    background-color: #2D2D2D;
                    color: white;
                }
                """
            )
        else:
            target.setStyleSheet(
                """
            QLabel {
                font-size: 20px;
                color: white; 
            }
            QPushButton {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QTextEdit, QListWidget {
                background-color: #2D2D2D;
                color: white;
            }
            """
            )

    def play_continuously(self):
        try:
            while True:  # While game not over
                self.play_week()
        except Exception as e:
            raise BBError(e, self) from e

    def make_dark_palette(self):
        # Dark Mode
        dark_palette = QPalette()

        # Set window background to dark gray
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))

        # Set window text to white
        dark_palette.setColor(QPalette.WindowText, Qt.white)

        # Set base color for widgets to black
        dark_palette.setColor(QPalette.Base, QColor(18, 18, 18))

        # Set text color for widgets to white
        dark_palette.setColor(QPalette.Text, Qt.white)

        # Set placeholder text color to dark gray
        dark_palette.setColor(QPalette.PlaceholderText, QColor(127, 127, 127))

        # Set highlighted text background to gray
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))

        # Set highlighted text color to black
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        return dark_palette

    def choose_houseguest(self):
        hg = next(h for h in self.houseguests if h.name == self.clicked_hg)
        item = self.houseguest_list_widget.findItems(self.clicked_hg, Qt.MatchExactly)[
            0
        ]

        item.setBackground(self.chosen_color)
        item.setFont(item.font())

        self.choose_hg_btn.setDisabled(True)
        self.houseguest_list_widget.itemClicked.disconnect()

        # Set the chosen houseguest
        self.chosen_hg = hg

        # Reset clicked houseguest
        self.clicked_hg = None

    def set_text_color_hglw(self):
        for i in range(self.houseguest_list_widget.count()):
            item = self.houseguest_list_widget.item(i)
            item.setForeground(self.no_color)

        for i in range(self.houseguest_list_widget.count()):
            in_nom = False
            item = self.houseguest_list_widget.item(i)
            name = item.text()
            hg = next(h for h in self.houseguests if h.name == name)
            
            if self.nominees:
                if hg in self.nominees:
                    in_nom = True

            if hg in self.evicted_houseguests:
                color = self.evicted_color
            elif self.veto_winner == hg:
                color = self.veto_color
            elif self.HOH == hg:
                color = self.hoh_color
            elif in_nom == True:
                color = self.noms_color
            else:
                color = self.no_color

            item.setForeground(color)

        # Clear the left list widget
        self.left_list_widget.clear()

        # Add title item
        title_item = QListWidgetItem("Big Brother (US)")
        bold_font = title_item.font()
        bold_font.setBold(True)
        title_item.setFont(bold_font)
        self.left_list_widget.addItem(title_item)

        # Add HOH item
        if self.HOH is not None:
            hoh_item = QListWidgetItem("HOH: ")
            if self.HOH:
                hoh_item.setText(f"HOH: {self.HOH.name}")
                hoh_item.setForeground(self.hoh_color)
            self.left_list_widget.addItem(hoh_item)

        # Add Nominees item
        if self.nominees is not None:
            noms_item = QListWidgetItem("Nominees: ")
            if self.noms_for_list:
                noms_text = ", ".join([nom.name for nom in self.noms_for_list])
                noms_item.setText(f"Nominees: {noms_text}")
                noms_item.setForeground(self.noms_color)
            self.left_list_widget.addItem(noms_item)

        # Add Veto Holder item
        if self.veto_winner is not None:
            veto_item = QListWidgetItem("Veto Holder: ")
            veto_item.setText(f"Veto Holder: {self.veto_winner.name}")
            veto_item.setForeground(self.veto_color)
            self.left_list_widget.addItem(veto_item)

        if self.used is not None:
            veto_used_item = QListWidgetItem("Veto Used: ")
            if self.used:
                veto_used_item.setText(f"Veto Used: Yes, on {self.nominee_saved.name}")
            else:
                veto_used_item.setText("Veto Used: No")
            veto_used_item.setForeground(self.veto_color)
            self.left_list_widget.addItem(veto_used_item)

        # Add Replacement Nominees item
        if self.renoms_for_list is not None:
            rnoms_item = QListWidgetItem("Replacement Nominees: ")
            if self.renoms_for_list:
                self.print_debug([self.renoms_for_list, self.nominees])
                if self.renoms_for_list != self.nominees:
                    rnoms_text = ", ".join([rnom.name for rnom in self.renoms_for_list])
                    rnoms_item.setText(f"Replacement Nominees: {rnoms_text}")
                    rnoms_item.setForeground(self.noms_color)
                else:
                    rnoms_item.setText(f"Nominees stayed the same.")
                    rnoms_item.setForeground(self.noms_color)
            self.left_list_widget.addItem(rnoms_item)

        # Add Evicted item
        if self.evicted is not None:
            evicted_item = QListWidgetItem("Evicted: ")
            if self.evicted:
                evicted_item.setText(f"Evicted: {self.evicted.name}")
                evicted_item.setForeground(self.evicted_color)
            self.left_list_widget.addItem(evicted_item)

    def print_debug(self, text):
        if self.settings.value("DebugMode", True, type=bool):
            # Print text
            print(text)

    def enable_button(self):
        self.next_week_btn.setEnabled(True)

    def create_players(self):
        n = []
        for i in range(self.num_players):
            name = names.get_first_name()
            while name in n:
                name = names.get_first_name()
            self.houseguests.append(HouseGuest(name))
            n.append(name)

    def do_impressions(self):
        for hg1 in self.houseguests:
            for hg2 in self.houseguests:
                if hg1 != hg2:
                    impression = random.randint(
                        1, 10
                    )  # Generate impressions between 1 and 10
                    hg1.impressions[hg2.name] = impression
        for hg in self.houseguests:
            self.print_debug([hg.name, hg.impressions])

    def show_impressions(self):
        # Create matrix if it doesn't exist (happens on reset also)
        self.matrix = ImpressionMatrix(self.houseguests)

        # Show matrix
        self.matrix.appear(self.houseguests)

    def introduce_players(self):
        self.print_text(f"Meet the {len(self.houseguests)} houseguests:")
        for player in self.houseguests:
            self.print_text(player.summary())

    def play_week(self):
        """Simulate a week of Big Brother"""
        self.text_box.clear()
        if self.end_state == 1:
            self.reset()
            return
        self.week += 1
        self.choose_hg_btn.setDisabled(True)
        tsl = self.title_season_label
        if self.retain_season:
            tsl.setText(f"Season {self.season_num}, Week {self.week}")
        else:
            tsl.setText(f"Week {self.week}")
        self.print_text(f"Week {self.week}:")

        if self.week > 1:
            self.reset_hgs()

        # FOR DEBUG
        self.print_debug(
            f"BEGINNING OF WEEK {self.week}. HOUSEGUESTS: {self.houseguests}"
        )

        # Check if only 2 players left
        # If more than 2 players, play regular week
        if len(self.houseguests) > 2:
            # Regular game play
            self.next_week_btn.setEnabled(False)
            self.select_HOH()
            self.set_text_color_hglw()
            self.events.event_spawner()
            self.select_noms()
            self.set_text_color_hglw()
            self.events.event_spawner()
            self.play_veto()
            self.set_text_color_hglw()
            self.events.event_spawner()
            self.veto_ceremony()
            self.set_text_color_hglw()
            self.events.event_spawner()
            self.eviction()
            self.events.event_spawner()
            self.set_text_color_hglw()
            self.text_box.clear()
            self.summarize_week()
            self.next_week_btn.setEnabled(True)

        else:
            self.finale()
            
    def finale(self):
        # Finale
        self.print_text(
            f"Final 2: {self.houseguests[0].name} and {self.houseguests[1].name}"
        )
        
        # Disable the "Proceed" and "Forward 1 Week" buttons
        self.proceed_btn.setEnabled(False)
        self.next_week_btn.setEnabled(False)

        # Increment the season number
        self.season_num += 1

        # Have them plead their case
        self.print_text(f"{self.houseguests[0].name} pleads their case...")
        self.print_text(f"{self.houseguests[1].name} pleads their case...")

        # Calculate number of jurors
        num_jurors = (NUM_PLAYERS // 2) + 1
        if num_jurors % 2 == 0:
            num_jurors += 1

        # Take the first num_jurors evicted houseguests as jurors
        jurors = self.evicted_houseguests[-num_jurors:]

        votes1 = 0
        votes2 = 0

        # Jury votes (This is just for their dialog before the voting happens)
        for juror in jurors:

            # Juror voting confessional dialog
            imp1 = juror.impressions[self.houseguests[0].name]
            imp2 = juror.impressions[self.houseguests[1].name]

            score_diff = abs(imp1 - imp2)

            if imp1 > imp2:
                higher_name = self.houseguests[0].name
            else:
                higher_name = self.houseguests[1].name

            if score_diff >= 8 and max(imp1, imp2) == 10:
                phrase = random.choice(FINALE_PHRASES[10]).format(name=higher_name)
            elif score_diff >= 6:
                phrase = random.choice(FINALE_PHRASES[8, 9]).format(
                    name=higher_name
                )
            elif score_diff >= 4:
                phrase = random.choice(FINALE_PHRASES[6, 7]).format(
                    name=higher_name
                )
            elif score_diff >= 2:
                phrase = random.choice(FINALE_PHRASES[4, 5]).format(
                    name=higher_name
                )
            else:
                phrase = random.choice(FINALE_PHRASES[2, 3]).format(
                    name=higher_name
                )

            self.print_text(f"{juror.name}: {phrase}")

        # Read votes (This is where the votes are actually cast)
        for juror in jurors:

            imp1 = juror.impressions[self.houseguests[0].name]
            imp2 = juror.impressions[self.houseguests[1].name]

            if imp1 == imp2:
                coin_flip = random.choice([0, 1])
                if coin_flip == 0:
                    votedfor = 0
                else:
                    votedfor = 1
            elif imp1 > imp2:
                votedfor = 0
            else:
                votedfor = 1

            if votedfor == 0:
                self.print_text(
                    f"{juror.name} voted for {self.houseguests[0].name} to win Big Brother!"
                )
                votes1 += 1
            else:
                self.print_text(
                    f"{juror.name} voted for {self.houseguests[1].name} to win Big Brother!"
                )
                votes2 += 1

        if votes1 > votes2:
            winner = self.houseguests[0]
            winvotes = votes1
            runvotes = votes2
            runner_up = self.houseguests[1]
        elif votes2 > votes1:
            winner = self.houseguests[1]
            runner_up = self.houseguests[0]
            winvotes = votes2
            runvotes = votes1
        else:
            winner = random.choice(self.houseguests)

        self.print_text(f"{winner.name} wins Big Brother!")
        # Remove evicted houseguest from the list
        for i in range(self.houseguest_list_widget.count()):
            self.print_text(self.houseguest_list_widget.item(i).text())
            if self.houseguest_list_widget.item(i).text() != winner.name:
                row = i
        self.houseguest_list_widget.takeItem(row)
        
        # Add winner, their votes, runner up, their votes, AFP to left widget
        winner_item = QListWidgetItem(f"Winner: {winner.name}")
        winner_item.setForeground(self.hoh_color)
        self.left_list_widget.addItem(winner_item)

        winner_votes_item = QListWidgetItem(f"Winner Votes: {winvotes}")
        winner_votes_item.setForeground(self.hoh_color)
        self.left_list_widget.addItem(winner_votes_item)

        runner_up_item = QListWidgetItem(f"Runner-Up: {runner_up.name}")
        runner_up_item.setForeground(self.noms_color)
        self.left_list_widget.addItem(runner_up_item)

        runner_up_votes_item = QListWidgetItem(f"Runner-Up Votes: {runvotes}")
        runner_up_votes_item.setForeground(self.noms_color)
        self.left_list_widget.addItem(runner_up_votes_item)

        # Change button text
        self.next_week_btn.setText("Next Season")
        self.end_state = 1

        if self.retain_season:
            self.season_num += 1

    def proceed(self):
        try:
            if self.step_index == 0:
                self.next_week_btn.setText("Forward 1 Week")
                self.next_week_btn.clicked.disconnect()
                self.next_week_btn.clicked.connect(self.play_week)
            if self.end_state == 1:
                self.reset()
                return
            if len(self.houseguests) > 2:
                self.step_by_step_mode = True
                self.next_step()
            else:
                self.finale()
        except Exception as e:
            raise BBError(e, self) from e

    def next_step(self):
        if self.step_index == 0:
            self.text_box.clear()
            if self.end_state == 1:
                self.reset()
                return
            self.week += 1
            self.choose_hg_btn.setDisabled(True)
            tsl = self.title_season_label
            if self.retain_season:
                tsl.setText(f"Season {self.season_num}, Week {self.week}")
            else:
                tsl.setText(f"Week {self.week}")
            self.print_text(f"Week {self.week}:")

            if self.week > 1:
                self.reset_hgs()

            # FOR DEBUG
            self.print_debug(
                f"BEGINNING OF WEEK {self.week}. HOUSEGUESTS: {self.houseguests}"
            )
            self.select_HOH()
            self.set_text_color_hglw()
            self.events.event_spawner()
            self.step_index += 1
            
        elif self.step_index == 1:
            self.select_noms()
            self.set_text_color_hglw()
            self.events.event_spawner()
            self.step_index += 1
            
        elif self.step_index == 2:
            self.play_veto()
            self.set_text_color_hglw()
            self.events.event_spawner()
            self.step_index += 1
            
        elif self.step_index == 3:
            self.veto_ceremony()
            self.events.event_spawner()
            self.set_text_color_hglw()
            self.step_index += 1
            
        elif self.step_index == 4:
            self.eviction()
            self.events.event_spawner()
            self.set_text_color_hglw()
            self.next_week_btn.setEnabled(True)
            self.next_week_btn.setText("Continue to Next Week")
            self.step_index = 0
            self.step_by_step_mode = False
            self.HOH = None
            self.nominees = None
            self.veto_winner = None
            self.used = None
            self.renoms_for_list = None
            
        else:
            print("Error. self.step_index set to invalid value. Returning to step one.")
            self.step_index = 0

        if self.step_by_step_mode:
            if self.step_index == 0:
                self.next_week_btn.setText("Forward 1 Week")
            else:
                self.next_week_btn.setText("Conclude Week")
                self.next_week_btn.clicked.disconnect()
                self.next_week_btn.clicked.connect(self.conclude_week)
            self.next_week_btn.setEnabled(True)

    def conclude_week(self):
        if self.step_index < 2:
            self.select_noms()
            self.events.event_spawner()

        if self.step_index < 3:
            self.play_veto()
            self.events.event_spawner()

        if self.step_index < 4:
            self.veto_ceremony()
            self.events.event_spawner()

        if self.step_index < 5:
            self.eviction()
            self.events.event_spawner()
            self.set_text_color_hglw()

        self.text_box.clear()
        self.summarize_week()
        
        self.next_week_btn.setText("Forward 1 Week")
        self.next_week_btn.clicked.disconnect()
        self.next_week_btn.clicked.connect(self.play_week)
        
        self.step_index = 0
        self.HOH = None
        self.nominees = None
        self.veto_winner = None
        self.used = None
        self.renoms_for_list = None

    def update_evicted(self):
        # Remove evicted houseguest from the list
        row = None
        for i in range(self.houseguest_list_widget.count()):
            if self.houseguest_list_widget.item(i).text() == self.evicted.name:
                row = i
        if row is not None:
            print("HERE")
            self.houseguest_list_widget.takeItem(row)
        self.houseguests.remove(self.evicted)
        self.evicted = None

    def reset_hgs(self):
        self.update_evicted()
        for hg in self.houseguests:
            hg.HOH = False
            hg.nominee = False
            hg.veto = False
            hg.vetoed = False
        self.HOH = None
        self.nominees = None
        self.veto_winner = None
        self.used = None 
        

    def select_HOH(self):
        # Choose HOH
        # Check if only 3 players left
        winner = self.comp("HOH")
        if len(self.houseguests) > 3:

            # Can't be HOH two weeks in a row
            potential_HOHs = [
                hg
                for hg in self.houseguests
                if hg not in self.evicted_houseguests and hg != self.prev_HOH
            ]

            if len(potential_HOHs) > 0:
                self.HOH = random.choice(potential_HOHs)
            else:
                self.HOH = random.choice(self.houseguests)

        else:
            self.HOH = random.choice(self.houseguests)

            # Update previous HOH
            self.prev_HOH = self.HOH

        self.HOH.HOH = True
        self.print_text(f"{self.HOH.name} is the new Head of Household")
        self.print_debug(f"HOH: {self.HOH.name}")

    def select_noms(self):
        # Nominate two players
        self.nominees = []

        worst_impressions = [
            (name, impression)
            for name, impression in sorted(
                self.HOH.impressions.items(), key=lambda x: x[1]
            )[:2]
            if name in {hg.name for hg in self.houseguests}
        ]

        for name, impression in worst_impressions:
            nominee = next(hg for hg in self.houseguests if hg.name == name)
            self.nominees.append(nominee)

        while len(self.nominees) < 2:

            potential_nominees = list(
                set(self.houseguests) - set([self.HOH]) - set(self.nominees)
            )
            if potential_nominees:
                if self.HOH.target in self.houseguests:
                    self.nominees.append(self.HOH.target)
                else:
                    self.nominees.append(random.choice(potential_nominees))

        for nominee in self.nominees:
            nominee.nominee = True

        self.print_debug(f"CURRENT NOMS: {self.nominees}")

        self.print_text(
            f"{self.HOH.name} has nominated {self.nominees[0].name} and {self.nominees[1].name} for eviction."
        )

        self.noms_for_list = deepcopy(self.nominees)

    def play_veto(self):
        # Check if there are more than 3 houseguests remaining
        if len(self.houseguests) > 3:
            # Play veto competition
            self.veto_winner = self.comp("Veto")
        else:
            # No veto competition
            self.print_text("There are only 3 houseguests remaining, so no veto competition will be held.")
            self.veto_winner = None

    def veto_ceremony(self):
        self.used = False
        if self.veto_winner is not None:
            # If there are 4 houseguests remaining and the veto winner is not HOH or nominated
            if (
                len(self.houseguests) == 4
                and self.veto_winner not in self.nominees
                and self.veto_winner != self.HOH
            ):
                self.print_text(
                    f"{self.veto_winner.name} has won the Power of Veto, but cannot use it."
                )
            else:
                # If veto winner is also a nominee, force them to use it on self
                if self.veto_winner in self.nominees:
                    self.print_text(
                        f"{self.veto_winner.name} has automatically used the Veto on themselves."
                    )
                    self.used = True
                    self.nominee_saved = self.veto_winner
                    self.nominee_saved.vetoed = True
                    self.nominees.remove(self.nominee_saved)
                    self.print_debug(f"VETO USED ON: {self.veto_winner.name}")
                else:
                    veto_used = random.choice([True, False])

                    if veto_used:
                        self.used = True
                        self.nominee_saved = random.choice(self.nominees)
                        self.print_text(
                            f"{self.veto_winner} has chosen to use the Power of Veto on {self.nominee_saved.name}."
                        )
                        self.print_debug(f"VETO USED ON: {self.nominee_saved.name}")

                        self.nominees.remove(self.nominee_saved)
                        self.nominee_saved.vetoed = True

                    else:
                        self.print_text(
                            f"{self.veto_winner} has chosen not to use the Power of Veto."
                        )

                if self.used:
                    # Replacement nominations
                    replacement_nom = None
                    potential_replacements = [
                        hg
                        for hg in self.houseguests
                        if hg
                        not in [
                            self.HOH,
                            self.veto_winner,
                            self.nominee_saved,
                            self.nominees[0],
                        ]
                    ]
                    self.print_debug(
                        f"POTENTIAL REPLACEMENT NOMINEES: {potential_replacements}"
                    )

                    if self.HOH.target and self.HOH.target in potential_replacements:
                        replacement_nom = self.HOH.target
                    elif len(self.HOH.alliances) > 0:
                        for hg in potential_replacements:
                            if all(a not in self.HOH.alliances for a in hg.alliances):
                                replacement_nom = hg
                                break

                    if replacement_nom == None:
                        replacement_nom = random.choice(potential_replacements)

                    self.nominees.append(replacement_nom)
                    self.print_text(
                        f"{self.HOH.name} has nominated {replacement_nom.name} as the replacement nominee."
                    )

        self.renoms_for_list = deepcopy(self.nominees)
        if self.renoms_for_list == self.noms_for_list:
            self.renoms_for_list = "No change"

    def eviction(self):
        # Eviction
        votes = {}
        for houseguest in set(self.houseguests) - set([self.HOH]):
            # Calculate the average impression of each nominee
            nominee_impressions = {}
            for nom in self.nominees:
                nominee_impressions[nom] = sum(
                    hg.impressions[nom.name]
                    for hg in self.houseguests
                    if nom.name in hg.impressions
                ) / len(self.houseguests)

            # Vote for the nominee with the lower average impression
            if houseguest.target:
                vote = houseguest.target
            else:
                temp = min(nominee_impressions, key=nominee_impressions.get)
                vote = temp.name
            votes[houseguest.name] = vote

        evicted_name = max(votes, key=list(votes.values()).count)
        evicted = next(hg for hg in self.houseguests if hg.name == evicted_name)
        # Update evicted houseguest
        self.evicted = evicted
        statement = " has been evicted from the Big Brother house."
        self.formatting[statement] = self.evict_statement_color
        self.print_text(f"{evicted.name}{statement}")
        self.evicted_houseguests.append(evicted)
        

        # Update targets after eviction
        for hg in self.houseguests:
            if hg.target == evicted.name:
                hg.target = None

        # Reset "vetoed" status
        for hg in self.houseguests:
            hg.vetoed = False

        # Find and remove any 1-person alliances
        to_delete = [a for a in self.alliances.values() if len(a.members) <= 1]
        for alliance in to_delete:
            # Remove from the houseguest's alliance list
            for hg in self.houseguests:
                if alliance.name in hg.alliances:
                    hg.alliances.remove(alliance.name)

            # Delete the alliance
            del self.alliances[alliance.name]

    def create_alliance(self):
        if len(self.houseguests) > 5:
            members = random.sample(self.houseguests, random.randint(2, 4))
            alliance_name = "The " + random.choice(
                ["Wolves", "Dragons", "Lions", "Snakes", "Eagles"]
            )
            alliance = Alliance(alliance_name)

            for member in members:
                alliance.add_member(member)

            self.alliances[alliance_name] = alliance

            self.print_text(
                f"{alliance_name} alliance forms between {', '.join([member.name for member in members])}."
            )

    # RESET ========================================
    def reset(self):
        self.houseguests = []
        self.evicted_houseguests = []
        self.prev_HOH = None
        self.matrix = None
        self.end_state = 0
        self.week = 0

        # Clear roles (used by UI)
        self.HOH = None
        self.nominees = None
        self.veto_winner = None
        self.used = None
        self.evicted = None
        self.renoms_for_list = None

        # Clear houseguest list
        self.houseguest_list_widget.clear()

        # Repopulate houseguests and list
        self.create_players()
        for hg in self.houseguests:
            self.houseguest_list_widget.addItem(hg.name)
        for h in self.houseguests:
            h.impressions = {}
        self.do_impressions()

        # Re-enable buttons
        self.choose_hg_btn.setDisabled(False)

        # Reset button text
        self.next_week_btn.setText("Continue")
        self.introduce_players()
        
        # Enable buttons
        self.proceed_btn.setEnabled(True)
        self.next_week_btn.setEnabled(True)

        # Reset button text
        self.next_week_btn.setText("Forward 1 Week")
        self.introduce_players()

        tsl = self.title_season_label
        if self.retain_season:
            tsl.setText(f"Season {self.season_num}")

    def show_preferences(self):
        # func for toggling the custom speed
        def toggle_custom_speed(self):
            index = print_speed_presets.currentIndex()
            if index == 3:
                print_speed_custom.setDisabled(False)
            else:
                print_speed_custom.setDisabled(True)
                if index == 0:
                    print_speed_custom.setValue(0)  # Reset value
                elif index == 1:
                    print_speed_custom.setValue(0.2)  # Reset value
                elif index == 2:
                    print_speed_custom.setValue(0.8)  # Reset value

        dialog = QDialog(self)
        layout = QVBoxLayout(dialog)
        self.retain_season = self.settings.value("RetainSeason", False)

        # Pick colors
        self.color_picker = QPushButton("Chosen HouseGuest Color")
        self.hoh_color_picker = QPushButton("HOH Color")
        self.noms_color_picker = QPushButton("Nominees Color")
        self.veto_color_picker = QPushButton("Veto Winner Color")
        self.evicted_color_picker = QPushButton("Evicted Color")

        self.color_picker.clicked.connect(lambda: self.pick_color("chosen"))
        self.hoh_color_picker.clicked.connect(lambda: self.pick_color("hoh"))
        self.noms_color_picker.clicked.connect(lambda: self.pick_color("noms"))
        self.veto_color_picker.clicked.connect(lambda: self.pick_color("veto"))
        self.evicted_color_picker.clicked.connect(lambda: self.pick_color("evicted"))

        # Add setting for NUM_PLAYERS
        num_players_label = QLabel("Number of Players: ")
        num_players_spinner = QSpinBox()
        num_players_spinner.setValue(self.settings.value("NUM_PLAYERS", 12))

        retain_season_cb = QCheckBox("Retain Previous Seasons")

        print_speed_label = QLabel("Print Speed:")
        print_speed_presets = QComboBox()
        print_speed_presets.addItems(["Instant", "Fast", "Slow", "Custom"])
        print_speed_custom = QDoubleSpinBox()
        print_speed_custom.setValue(0)
        print_speed_presets.currentIndexChanged.connect(toggle_custom_speed)
        print_speed_custom.setDisabled(True)

        step_by_step_cb = QCheckBox("Step-by-Step Mode")
        step_by_step_cb.setChecked(
            self.settings.value("StepByStepMode", False, type=bool)
        )

        debug_mode_cb = QCheckBox("Debug Mode")
        debug_mode_cb.setChecked(self.settings.value("DebugMode", False, type=bool))

        # Add other settings...

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(num_players_label)
        layout.addWidget(num_players_spinner)
        layout.addWidget(retain_season_cb)
        layout.addWidget(self.color_picker)
        layout.addWidget(self.hoh_color_picker)  # Add this line
        layout.addWidget(self.noms_color_picker)  # Add this line
        layout.addWidget(self.veto_color_picker)  # Add this line
        layout.addWidget(self.evicted_color_picker)  # Add this line

        layout.addWidget(print_speed_label)
        layout.addWidget(print_speed_presets)
        layout.addWidget(print_speed_custom)
        # Add other widgets...

        layout.addWidget(step_by_step_cb)
        layout.addWidget(debug_mode_cb)
        layout.addWidget(button_box)

        dark_palette = self.make_dark_palette()

        self.dark_style_sheet(dialog)
        dialog.setPalette(dark_palette)

        if dialog.exec() == QDialog.Accepted:
            ind = print_speed_presets.currentIndex()
            custom_speed = print_speed_custom.value()
            self.settings.setValue("NUM_PLAYERS", num_players_spinner.value())
            self.settings.setValue("RetainSeason", retain_season_cb.isChecked())
            self.settings.setValue("StepByStepMode", step_by_step_cb.isChecked())
            self.update_print_speed(ind, custom_speed)
            self.settings.setValue("DebugMode", debug_mode_cb.isChecked())
            self.settings.sync()
            self.step_by_step_mode = step_by_step_cb.isChecked()

            # Save other settings...

    def pick_color(self, target):
        color = QColorDialog.getColor()
        if color.isValid():
            if target == "chosen":
                self.chosen_color = color
                self.color_picker.setStyleSheet(
                    f"""
                    background-color: {self.chosen_color.name()}; 
                    color: {self.chosen_color.lightness() > 128 and 'black' or 'white'};"""
                )
            elif target == "hoh":
                self.hoh_color = color
                self.hoh_color_picker.setStyleSheet(
                    f"""
                    background-color: {self.hoh_color.name()}; 
                    color: {self.hoh_color.lightness() > 128 and 'black' or 'white'};"""
                )
            elif target == "noms":
                self.noms_color = color
                self.noms_color_picker.setStyleSheet(
                    f"""
                    background-color: {self.noms_color.name()}; 
                    color: {self.noms_color.lightness() > 128 and 'black' or 'white'};"""
                )
            elif target == "veto":
                self.veto_color = color
                self.veto_color_picker.setStyleSheet(
                    f"""
                    background-color: {self.veto_color.name()}; 
                    color: {self.veto_color.lightness() > 128 and 'black' or 'white'};"""
                )
            elif target == "evicted":
                self.evicted_color = color
                self.evicted_color_picker.setStyleSheet(
                    f"""
                    background-color: {self.evicted_color.name()}; 
                    color: {self.evicted_color.lightness() > 128 and 'black' or 'white'};"""
                )

    def update_print_speed(self, index, csp):
        if index == 0:  # Slow
            self.print_speed = 0.8
        elif index == 1:  # Fast
            self.print_speed = 0.2
        elif index == 2:  # Instant
            self.print_speed = 0
        else:
            self.print_speed = csp

    def comp(self, v):
        if v == "HOH":
            comps = HOH_COMPS
            comp_name = random.choice(comps)
            hoh_text = f"The houseguests compete in the {comp_name} HOH competition."
            self.formatting[hoh_text] = self.hoh_color
            self.print_text(hoh_text)

            # Simulate the competition
            participants = [hg for hg in self.houseguests if hg != self.prev_HOH]
            random.shuffle(participants)
            winner = None

            for i in range(len(participants)):
                houseguest = participants[i]
                if i == len(participants) - 1:
                    winner = houseguest
                    self.print_text(f"{houseguest} wins the {comp_name} HOH competition!")
                else:
                    self.print_text(f"{houseguest} is out of the competition.", False)

            return winner

        elif v == "Veto":
            comp_name = random.choice(VETO_COMPS)
            veto_text = f"The houseguests compete in the {comp_name} veto competition."
            self.formatting[veto_text] = self.veto_color
            self.print_text(veto_text)
            
            # Select participants for the veto competition
            participants = [self.HOH] + self.nominees
            remaining_houseguests = [hg for hg in self.houseguests if hg not in participants]
            num_random_players = 3
            houseguest_choice_drawn = False

            while len(participants) < 6 and len(remaining_houseguests) > 0:
                if not houseguest_choice_drawn and random.random() < 1 / (len(self.houseguests) - len(participants) + 1):
                    chooser = random.choice(participants)
                    chosen_houseguest = max(remaining_houseguests, key=lambda hg: hg.impressions[chooser.name])
                    participants.append(chosen_houseguest)
                    remaining_houseguests.remove(chosen_houseguest)
                    self.print_text(f"{chooser} draws houseguest choice and selects {chosen_houseguest} to play in the veto competition.")
                    houseguest_choice_drawn = True
                else:
                    random_player = random.choice(remaining_houseguests)
                    participants.append(random_player)
                    remaining_houseguests.remove(random_player)
                    self.print_text(f"{random_player} is randomly selected to play in the veto competition.")

            # Simulate the competition
            random.shuffle(participants)
            winner = None

            for i in range(len(participants)):
                houseguest = participants[i]
                if i == len(participants) - 1:
                    winner = houseguest
                    self.print_text(f"{houseguest} wins the {comp_name} veto competition!")
                else:
                    self.print_text(f"{houseguest} is out of the competition.")

            return winner

        else:
            return None

    def edit_hg_name(self, item):
        # Get houseguest object
        name = item.text()
        hg = next(h for h in self.houseguests if h.name == name)

        # Create dialog
        dialog = EditNameDialog(hg.name, self)
        if dialog.exec() == QDialog.Accepted:
            # Update name
            new_name = dialog.get_name()
            hg.name = new_name
            item.setText(hg.name)

            # Update names in impressions dictionary
            for h in self.houseguests:
                if name in h.impressions:
                    h.impressions[new_name] = h.impressions.pop(name)

    def check_impressions(self, impr, hgname):
        if impr[hgname] < 0:
            impr[hgname] = 0
        if impr[hgname] > 10:
            impr[hgname] = 10

    def resizeEvent(self, event):

        # Get current widths
        col1_width = self.left_widget.width()
        col2_width = self.houseguest_list_widget.width()
        col3_width = self.text_box.width()

        # Calculate additional width to distribute
        available_width = self.width() - col1_width - col2_width - col3_width

        # Distribute extra width
        added_width = available_width / 3

        # Set new widths
        new_col1_width = col1_width + added_width
        self.left_widget.setFixedWidth(int(new_col1_width))

        # Set new widths
        new_col2_width = col2_width + added_width
        self.left_widget.setFixedWidth(int(new_col2_width))

        # Set new widths
        new_col3_width = col3_width + added_width
        self.left_widget.setFixedWidth(int(new_col3_width))
        
    def summarize_week(self):
        summary = f"WEEK SUMMARY:\n"
        
        if self.HOH:
            summary += f"- HOH: {self.HOH.name}\n"
        
        if self.nominees:
            summary += f"- Nominees: {', '.join([n.name for n in self.nominees])}\n"
            
        if self.veto_winner:
            summary += f"- Veto Winner: {self.veto_winner.name}\n"
            
        if self.used: 
            summary += f"- Veto Used: {self.used}\n"
            
        if self.renoms_for_list:
            if self.renoms_for_list != self.nominees:
                summary += f"- Replacement Nominees: {', '.join([r.name for r in self.renoms_for_list])}\n"
            
        if self.evicted:
            summary += f"- Evicted: {self.evicted.name}\n"
            
        # Print summary 
        self.print_text(summary)
        
    def print_text(self, text, nl=True):
        self.utility.print_text(text, nl)

    def make_formatting(self):
        self.utility.make_formatting()
        
    def show_showmances(self):
        showmance_dialog = QDialog(self)
        showmance_dialog.setWindowTitle("Showmances")
        layout = QVBoxLayout(showmance_dialog)

        self.showmances_list_widget = QListWidget()
        for hg1, hg2 in self.showmances:
            self.showmances_list_widget.addItem(f"{hg1.name} and {hg2.name}")

        layout.addWidget(self.showmances_list_widget)
        showmance_dialog.exec_()
        
    def show_alliances(self):
        alliance_dialog = QDialog(self)
        alliance_dialog.setWindowTitle("Alliances")
        layout = QVBoxLayout(alliance_dialog)

        alliance_list = QListWidget()
        for alliance in self.alliances.values():
            alliance_list.addItem(f"{alliance.name}: {', '.join([member.name for member in alliance.members])}")

        layout.addWidget(alliance_list)
        alliance_dialog.exec_()


class NoFocusDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        option.state &= ~QStyle.State_HasFocus
        super().paint(painter, option, index)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QApplication.font()
    font.setPointSize(14)
    app.setFont(font)

    ex = BigBrother()
    QApplication.instance().screenAdded.connect(ex.resizeEvent)
    sys.exit(app.exec_())

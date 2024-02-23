import random
import re
import sys
from copy import deepcopy

import names
from constants import *
from customtextedit import CustomTextEdit
from houseguest import HouseGuest
from impression_matrix import ImpressionMatrix
from name_edit import EditNameDialog
from PyQt5.QtCore import QSettings, Qt, QTimer
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QColorDialog,
                             QComboBox, QDialog, QDialogButtonBox,
                             QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem, QMenuBar,
                             QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
                             QStyle, QStyledItemDelegate, QTextEdit,
                             QVBoxLayout, QWidget)


class Alliance:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.target = None

    def add_member(self, houseguest):
        self.members.append(houseguest)

    def set_target(self, target):
        self.target = target


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
        self.end_state = 0
        self.events = []  # Initialize a list to store events
        self.alliances = {}  # Initialize a dictionary to store alliances
        self.settings = QSettings("Company Name", "App Name")
        self.num_players = NUM_PLAYERS
        self.print_speed = 0.8
        self.season_num = 1
        self.chosen_hg = None
        self.chosen_color = QColor(220, 220, 220)  # Beige
        self.clicked_hg = None
        self.week = 0
        self.noms_for_list = None
        self.renoms_for_list = None
        self.create_players()
        self.do_impressions()
        self.initUI()
        self.make_formatting()
        self.introduce_players()

    def initUI(self):
        # Create the QListWidget and add all houseguests
        self.setMinimumSize(1200, 800)

        # Colors
        self.chosen_color = QColor(220, 220, 220)
        self.hoh_color = QColor("#FFFF00")  # Yellow
        self.noms_color = QColor("#DC143C")  # Crimson
        self.veto_color = QColor("#FFA500")  # Orange
        self.evicted_color = QColor("#4B0082")  # Indigo
        self.no_color = QColor("#FFFFFF")
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
        #layout.addWidget(self.left_widget)

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

        # Add Continue button
        self.next_week_btn = QPushButton("Continue")
        self.next_week_btn.clicked.connect(self.play_week)

        # Add reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.next_week_btn)
        button_layout.addWidget(self.impressions_btn)
        button_layout.addWidget(self.reset_btn)

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

    def set_text_color(self):
        for i in range(self.houseguest_list_widget.count()):
            item = self.houseguest_list_widget.item(i)
            item.setForeground(self.no_color)

        for i in range(self.houseguest_list_widget.count()):
            item = self.houseguest_list_widget.item(i)
            name = item.text()
            hg = next(h for h in self.houseguests if h.name == name)

            if hg in self.evicted_houseguests:
                color = self.evicted_color
            elif hg.veto:
                color = self.veto_color
            elif hg.HOH:
                color = self.hoh_color
            elif hg.nominee:
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
        hoh_item = QListWidgetItem("HOH: ")
        if self.HOH:
            hoh_item.setText(f"HOH: {self.HOH.name}")
            hoh_item.setForeground(self.hoh_color)
        self.left_list_widget.addItem(hoh_item)

        # Add Nominees item
        noms_item = QListWidgetItem("Nominees: ")
        if self.noms_for_list:
            noms_text = ", ".join([nom.name for nom in self.noms_for_list])
            noms_item.setText(f"Nominees: {noms_text}")
            noms_item.setForeground(self.noms_color)
        self.left_list_widget.addItem(noms_item)

        # Add Veto Holder item
        veto_item = QListWidgetItem("Veto Holder: ")
        if self.veto_winner and self.veto_winner.name != self.HOH.name:
            veto_item.setText(f"Veto Holder: {self.veto_winner.name}")
            veto_item.setForeground(self.veto_color)
        self.left_list_widget.addItem(veto_item)

        # Add Replacement Nominees item
        rnoms_item = QListWidgetItem("Replacement Nominees: ")
        if self.renoms_for_list:
            rnoms_text = ", ".join([rnom.name for rnom in self.renoms_for_list])
            rnoms_item.setText(f"Replacement Nominees: {rnoms_text}")
            rnoms_item.setForeground(self.noms_color)
        self.left_list_widget.addItem(rnoms_item)

        # Add Evicted item
        evicted_item = QListWidgetItem("Evicted: ")
        if self.evicted:
            evicted_item.setText(f"Evicted: {self.evicted.name}")
            evicted_item.setForeground(self.evicted_color)
        self.left_list_widget.addItem(evicted_item)

    # Print text to box instead of console
    def print_text(self, text, nl=True):
        print(text)
        if "HOH:" in text:
            self.formatting["HOH:"] = self.hoh_color.name()
        if self.HOH is not None:
            self.formatting[self.HOH.name] = self.hoh_color.name()
        if "is the new Head of Household" in text:
            self.formatting["is the new Head of Household"] = self.hoh_color.name()

        for nom in self.nominees:
            self.formatting[nom.name] = self.noms_color.name()

        if "veto holder" in text:
            self.formatting["veto holder"] = self.veto_color.name()
        if "veto" in text:
            self.formatting["veto"] = self.veto_color.name()
        if self.veto_winner is not None and self.veto_winner.name != self.HOH.name:
            self.formatting[self.veto_winner.name] = self.veto_color.name()

        if self.evicted:
            self.formatting[self.evicted.name] = self.evicted_color.name()

        if nl:
            self.text_box.appendFormattedText(text + "\n", self.formatting)
        else:
            self.text_box.appendFormattedText(text, self.formatting)

        if self.print_speed > 0:
            QTimer.singleShot(int(self.print_speed * 1000), self.enable_button)

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
            print(hg.name, hg.impressions)

    def make_formatting(self):
        self.formatting = {
            "HOH:": self.hoh_color,
            "is the new Head of Household": self.hoh_color,
            # Add other formatting tags and colors here
        }
        for hg in self.houseguests:
            self.formatting[hg.name] = self.no_color

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
            self.update_evicted()
            self.reset_hgs()

        # Check if only 2 players left
        # If more than 2 players, play regular week
        if len(self.houseguests) > 2:
            # Regular game play
            self.next_week_btn.setEnabled(False)
            self.select_HOH()
            self.set_text_color()
            self.event_spawner()
            self.select_noms()
            self.set_text_color()
            self.event_spawner()
            self.play_veto()
            self.set_text_color()
            self.event_spawner()
            self.veto_ceremony()
            self.set_text_color()
            self.event_spawner()
            self.eviction()
            self.event_spawner()
            self.set_text_color()
            self.next_week_btn.setEnabled(True)

        else:
            # Finale
            self.print_text(
                f"Final 2: {self.houseguests[0].name} and {self.houseguests[1].name}"
            )

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

            # Change button text
            self.next_week_btn.setText("Next Season")
            self.end_state = 1

            if self.retain_season:
                self.season_num += 1

    def update_evicted(self):
        # Remove evicted houseguest from the list
        row = None
        for i in range(self.houseguest_list_widget.count()):
            if self.houseguest_list_widget.item(i).text() == self.evicted.name:
                row = i
        if row is not None:
            self.houseguest_list_widget.takeItem(row)
        self.houseguests.remove(self.evicted)
        self.evicted = None

    def reset_hgs(self):
        for hg in self.houseguests:
            hg.HOH = False
            hg.nominee = False
            hg.veto = False
            hg.vetoed = False

    def select_HOH(self):
        # Choose HOH
        # Check if only 3 players left
        self.comp("HOH")
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
        print(self.nominees)

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

        print(self.nominees)

        self.print_text(
            f"{self.HOH.name} has nominated {self.nominees[0].name} and {self.nominees[1].name} for eviction."
        )

        self.noms_for_list = deepcopy(self.nominees)

    def play_veto(self):
        # Play veto competition
        self.comp("Veto")
        NUM_VETO_PLAYERS = 6

        # updated veto competition section
        potential_players = list(
            set(self.houseguests) - set(self.nominees + [self.HOH])
        )

        if len(self.houseguests) > 3:
            veto_players = random.sample(
                potential_players,
                k=min(len(potential_players), NUM_VETO_PLAYERS - 3),
            )
            veto_players.extend(self.nominees + [self.HOH])
            self.veto_winner = random.choice(veto_players)
            self.print_text(f"{self.veto_winner} has won the Power of Veto!")

        else:
            self.veto_winner = None

        return potential_players

    def veto_ceremony(self):
        used = False
        if self.veto_winner is not None:
            # If veto winner is also a nominee, force them to use it on self
            if self.veto_winner in self.nominees:
                self.print_text(
                    f"{self.veto_winner.name} has automatically used the Veto on themselves."
                )
                used = True
                nominee_saved = self.veto_winner
                nominee_saved.vetoed = True
                self.nominees.remove(nominee_saved)
            else:
                veto_used = random.choice([True, False])

                if veto_used:
                    used = True
                    nominee_saved = random.choice(self.nominees)
                    self.print_text(
                        f"{self.veto_winner} has chosen to use the Power of Veto on {nominee_saved.name}."
                    )

                    self.nominees.remove(nominee_saved)
                    nominee_saved.vetoed = True

                else:
                    self.print_text(
                        f"{self.veto_winner} has chosen not to use the Power of Veto."
                    )

            if used:
                # Replacement nominations
                replacement_nom = None
                potential_replacements = [
                    hg
                    for hg in self.houseguests
                    if hg
                    not in [self.HOH, self.veto_winner, nominee_saved, self.nominees[0]]
                ]

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
                try:
                    self.print_text(
                        f"{self.HOH.name} has nominated {replacement_nom.name} as the replacement nominee."
                    )
                except:
                    print(replacement_nom)
                    print(self.houseguests)
                    print()

        else:
            pass

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
        self.print_text(f"{evicted.name} has been evicted from the Big Brother house.")
        self.evicted_houseguests.append(evicted)
        # Update evicted houseguest
        self.evicted = evicted

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
        self.houseguest_list_widget.clear()
        self.evicted_houseguests = []
        self.prev_HOH = None
        self.matrix = None
        self.end_state = 0  # Add this line
        self.week = 0

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
        layout.addWidget(button_box)

        dark_palette = self.make_dark_palette()

        self.dark_style_sheet(dialog)
        dialog.setPalette(dark_palette)

        if dialog.exec() == QDialog.Accepted:
            ind = print_speed_presets.currentIndex()
            custom_speed = print_speed_custom.value()
            self.settings.setValue("NUM_PLAYERS", num_players_spinner.value())
            self.settings.setValue("RetainSeason", retain_season_cb.isChecked())
            self.update_print_speed(ind, custom_speed)
            self.settings.sync()
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
            comps = [
                "Flip the House",
                "Majority Rules",
                "Question the Quack",
                "Counting Sheep",
                "True or False",
                "Memory Lane",
                "Slip 'n Slide",
                "Red Light, Green Light",
                "Egg Heads",
                "Spelling Bee",
            ]
        elif v == "Veto":
            comps = [
                "Block the Veto",
                "Knight Moves",
                "Cry Me a Veto",
                "Counting Votes",
                "Fact or Fiction",
                "Photographic Memory",
                "Slip 'n Veto",
                "Red Veto, Green Veto",
                "Egg on Your Face",
                "Spelling Veto",
            ]
        else:
            return

        self.print_text(
            "The houseguests compete in the " + random.choice(comps) + " competition."
        )

        for hg1 in self.houseguests:
            for hg2 in self.houseguests:
                if hg1 != hg2:
                    adjustment = random.randint(-1, 1)
                    hg1.impressions[hg2.name] += adjustment
                    hg2.impressions[hg1.name] += adjustment

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

    # EVENTS ==================================================================
    def event_spawner(self, variety=None):
        if variety is not None:
            self.houseguests = self.comp(self.houseguests, variety)
        else:
            # Random events
            for _ in range(random.randint(0, MAX_EVENTS)):
                event_index = random.randint(0, 3)
                if event_index == 0 and len(self.houseguests) >= 3:
                    hg1, hg2, hg3 = random.sample(self.houseguests, 3)
                    self.event_1(hg1, hg2, hg3)
                elif event_index == 1:
                    hg1, hg2 = random.sample(self.houseguests, 2)
                    self.event_2(hg1, hg2)
                elif event_index == 2 and len(self.houseguests) >= 2:
                    hg1, hg2 = random.sample(self.houseguests, 2)
                    if len(hg1.alliances) > 0:
                        self.event_3(hg1, hg2)
                    elif len(self.houseguests) >= 6:
                        self.event_5(hg1)
                    else:
                        self.event_4(hg1, hg2)
                else:
                    hg1, hg2 = random.sample(self.houseguests, 2)
                    self.event_4(hg1, hg2)

    def event_1(self, hg1, hg2, hg3):
        if hg1.manipulativeness >= random.randint(0, hg2.emotionality):
            hg2.target = hg3.name
            self.print_text(f"{hg2.name} was swayed!")

        # Opinion changes
        if hg1.impressions[hg3.name] >= 5:
            hg1.impressions[hg3.name] = min(10, hg1.impressions[hg3.name] + 1)
            hg2.impressions[hg3.name] = max(0, min(10, hg2.impressions[hg3.name] + 2))
        else:
            hg1.impressions[hg3.name] = max(0, hg1.impressions[hg3.name] - 1)
            hg2.impressions[hg3.name] = max(0, hg2.impressions[hg3.name] - 2)

        self.print_text(f"{hg1.name} pulls {hg2.name} aside to talk about {hg3.name}.")

    def event_2(self, hg1, hg2):
        if hg1.friendliness < hg2.emotionality:
            hg1.target = hg2.name
            hg2.target = hg1.name
            self.print_text(f"{hg1.name} and {hg2.name} were swayed!")

        # Opinion changes
        if random.random() < 0.8:
            hg1.impressions[hg2.name] = max(0, hg1.impressions[hg2.name] - 3)
            hg2.impressions[hg1.name] = max(0, hg2.impressions[hg1.name] - 3)

        topic = random.choice(
            [
                "the dishes",
                "who ate the last slice of pizza",
                "who flirts too much",
                "who snores",
            ]
        )
        self.print_text(f"{hg1.name} gets in a fight with {hg2.name} over {topic}!")

    def event_3(self, hg1, hg2):
        pick = None

        potential_alliances = []
        for alliance_name in hg1.alliances:
            alliance = self.alliances[alliance_name]
            if hg2 not in alliance.members:
                potential_alliances.append(alliance)

        if potential_alliances:
            alliance = random.choice(potential_alliances)

        if pick != None:
            self.print_text(
                f"{hg1.name} makes plans with {alliance.name} to target {hg2.name}."
            )

            for member in alliance.members:
                if member.name in self.houseguests:
                    if member.loyalty > hg1.manipulativeness:
                        member.target = hg2.name
                        print(self.houseguests)
                        print(member.impressions)
                        print(member.name, member.name in self.houseguests)
                        member.impressions[hg1.name] += 2
                        member.impressions[hg2.name] -= random.randint(2, 4)
                        self.check_impressions(member.impressions, hg1.name)
                        self.check_impressions(member.impressions, hg2.name)
                        self.print_text(f"{member.name} was convinced.")

    def event_4(self, hg1, hg2):
        # Opinion changes
        hg1.impressions[hg2.name] = min(
            10, hg1.impressions[hg2.name] + random.randint(0, 3)
        )
        hg2.impressions[hg1.name] = min(
            10, hg2.impressions[hg1.name] + random.randint(0, 3)
        )
        self.print_text(f"{hg1.name} has a casual conversation with {hg2.name}.")

    import re

    def event_5(self, hg1):
        alliance_size = random.randint(2, len(self.houseguests) // 2)
        alliance_members = random.sample(self.houseguests, alliance_size)

        alliance_name = self.generate_alliance_name(alliance_members)
        alliance = Alliance(alliance_name)

        for member in alliance_members:
            alliance.add_member(member)
            member.join_alliance(alliance)

        self.alliances[alliance_name] = alliance

        self.print_text(
            f"{alliance_name} alliance forms between {', '.join([member.name for member in alliance_members])}."
        )

    def generate_alliance_name(self, members):
        if random.random() < 0.3:
            return random.choice(["The Leftovers", "The Outsiders", "The Misfits"])

        names = [
            re.sub(r"([A-Z])", r" \1", member.name[0]).split() for member in members
        ]
        return "".join([random.choice(name) for name in names]).upper()

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

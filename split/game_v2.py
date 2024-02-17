import random
import sys

import names
from constants import *
from houseguest import HouseGuest
from impression_matrix import ImpressionMatrix
from name_edit import EditNameDialog
from PyQt5.QtCore import QSettings, Qt, QTimer
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QMenuBar, QPushButton, QSizePolicy,
                             QSpacerItem, QSpinBox, QTextEdit, QVBoxLayout,
                             QWidget)


class BigBrother(QWidget):

    def __init__(self):
        super().__init__()
        self.num_players = NUM_PLAYERS
        self.houseguests = []
        self.evicted_houseguests = []
        self.prev_HOH = None
        self.end_state = 0
        self.events = []  # Initialize a list to store events
        self.alliances = {}  # Initialize a dictionary to store alliances
        self.settings = QSettings("Company Name", "App Name")
        self.num_players = NUM_PLAYERS
        self.print_speed = 0.8
        self.season_num = 1
        self.create_players()
        self.do_impressions()
        self.initUI()
        self.introduce_players()

    def initUI(self):
        # Create the QListWidget and add all houseguests
        self.list_items = []
        self.houseguest_list = QListWidget()
        for hg in self.houseguests:
            self.houseguest_list.addItem(hg.name)
            self.list_items.append(hg.name)
        self.houseguest_list.itemDoubleClicked.connect(self.edit_hg_name)
        self.retain_season = self.settings.value("RetainSeason", defaultValue=False)

        # Set layout
        overall = QVBoxLayout()
        layout = QHBoxLayout()

        # Create widget for left side
        self.left_widget = QWidget()

        # Set fixed size
        self.left_widget.setFixedSize(250, 400)

        # Layout for labels on left
        self.left_layout = QVBoxLayout()

        self.title_season_label = QLabel("Big Brother (US)")
        self.hoh_label = QLabel("HOH: ")
        self.nominees_label = QLabel("NOMS: ")

        """ self.next_week_btn = QPushButton("Continue")
        self.next_week_btn.clicked.connect(self.play_week) """

        # Create menu bar
        menu_bar = QMenuBar()
        menu_bar.setMinimumSize(600, 0)  # Set minimum width to 600px
        menu_bar.setContentsMargins(20, 0, 20, 0)  # Left/right margins of 20px
        layout.setMenuBar(menu_bar)

        layout.setContentsMargins(0, 30, 0, 0)

        # Create File menu
        file_menu = menu_bar.addMenu("File")

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

        # Add "Impressions" button
        self.impressions_btn = QPushButton("Impressions")
        self.impressions_btn.clicked.connect(self.show_impressions)

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.title_season_label)
        self.left_layout.addWidget(self.hoh_label)
        self.left_layout.addWidget(self.nominees_label)
        # Add veto holder label
        self.veto_holder_label = QLabel("VETO: ")

        # Add replacement nominees label
        self.replacement_nominees_label = QLabel("R.NOMS: ")

        # Add evicted houseguest label
        self.evicted_label = QLabel("EVICT: ")

        self.left_layout.addWidget(self.veto_holder_label)
        self.left_layout.addWidget(self.replacement_nominees_label)

        self.left_layout.addWidget(self.evicted_label)

        # Layout for list on right
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.houseguest_list)

        # Set the layout on the widget
        self.left_widget.setLayout(self.left_layout)

        # Then add the widget to the main layout
        layout.addWidget(self.left_widget)

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

        overall.addLayout(layout)
        overall.addLayout(button_layout)

        # Add text display box
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)

        # Layout for list and text on right
        right_layout = QHBoxLayout()

        right_layout.addWidget(self.houseguest_list)

        right_layout.addWidget(self.text_box)

        layout.addLayout(right_layout)

        self.setLayout(overall)
        
        self.dark_style_sheet("self")

        dark_palette = self.make_dark_palette()

        self.setPalette(dark_palette)
        self.show()
        
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

    # Print text to box instead of console
    def print_text(self, text, nl=True):
        if nl is True:
            self.text_box.append(text + "\n")
        else:
            self.text_box.append(text)
        if self.print_speed > 0:
            QTimer.singleShot(int(self.print_speed * 1000), self.enable_button)

    def enable_button(self):
        self.next_week_btn.setEnabled(True)

    def create_players(self):
        for i in range(self.num_players):
            name = names.get_first_name()
            self.houseguests.append(HouseGuest(name))

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
        self.week = self.num_players - len(self.houseguests) + 1
        tsl = self.title_season_label
        if self.retain_season:
            tsl.setText(f"Season {self.season_num}, Week {self.week}")
        else:
            tsl.setText(f"Week {self.week}")
        self.print_text(f"Week {self.week}:")

        if self.end_state == 1:
            self.reset()

        # Check if only 2 players left
        # If more than 2 players, play regular week
        if len(self.houseguests) > 2:
            # Regular game play
            self.next_week_btn.setEnabled(False)
            self.select_HOH()
            self.event_spawner()
            nominees = self.select_noms()
            self.event_spawner()
            pp = self.play_veto(nominees)
            self.event_spawner()
            self.veto_ceremony(nominees, pp)
            self.event_spawner()
            self.eviction(nominees)
            self.event_spawner()
            self.next_week_btn.setEnabled(True)

        else:
            # Finale 
            self.print_text(f"Final 2: {self.houseguests[0].name} and {self.houseguests[1].name}")

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
                    phrase = random.choice(FINALE_PHRASES[8,9]).format(name=higher_name)
                elif score_diff >= 4:
                    phrase = random.choice(FINALE_PHRASES[6,7]).format(name=higher_name) 
                elif score_diff >= 2:
                    phrase = random.choice(FINALE_PHRASES[4,5]).format(name=higher_name)
                else:
                    phrase = random.choice(FINALE_PHRASES[2,3]).format(name=higher_name)
                    
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
                    self.print_text(f"{juror.name} voted for {self.houseguests[0].name} to win Big Brother!")
                    votes1 += 1
                else:
                    self.print_text(f"{juror.name} voted for {self.houseguests[1].name} to win Big Brother!")
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
            # Clear all labels except first
            for i in range(1, self.left_layout.count()):
                self.left_layout.itemAt(i).widget().setText("")
            # Remove evicted houseguest from the list
            for i in range(self.houseguest_list.count()):
                self.print_text(self.houseguest_list.item(i).text())
                if self.houseguest_list.item(i).text() != winner.name:
                    row = i
            self.houseguest_list.takeItem(row)

            # Set winner text
            self.hoh_label.setText(f"{winner.name} wins!")
            self.nominees_label.setText(f"{winner.name} received {winvotes} to win.")
            self.veto_holder_label.setText(f"{runner_up.name} received {runvotes} to win.")
            # TODO: Change r.noms text to AFP
            self.evicted_label.setText("Thanks for watching!")

            # Change button text
            self.next_week_btn.setText("Next Season")
            self.end_state = 1
            
            if self.retain_season:
                self.season_num += 1

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
        self.hoh_label.setText(f"HOH: {self.HOH.name}")

    def select_noms(self):
        # Nominate two players
        nominees = []

        worst_impressions = [
            (name, impression)
            for name, impression in sorted(
                self.HOH.impressions.items(), key=lambda x: x[1]
            )[:2]
            if name in {hg.name for hg in self.houseguests}
        ]

        for name, impression in worst_impressions:
            nominee = next(hg for hg in self.houseguests if hg.name == name)
            nominees.append(nominee)

        if len(nominees) < 2:

            potential_nominees = list(
                set(self.houseguests) - set([self.HOH]) - set(nominees)
            )
            if potential_nominees:
                if self.HOH.target and self.HOH.target not in self.houseguests:
                    nominees.append(random.choice(potential_nominees))
                else:
                    nominees.append(random.choice(potential_nominees))

                potential_nominees.remove(nominees[-1])
                if potential_nominees:
                    nominees.append(random.choice(potential_nominees))

        for nominee in nominees:
            nominee.nominee = True

        self.print_text(
            f"{self.HOH.name} has nominated {nominees[0].name} and {nominees[1].name} for eviction."
        )
        self.nominees_label.setText(
            f"NOMS: {', '.join([nom.name for nom in nominees])}"
        )

        return nominees

    def play_veto(self, nominees):
        # Play veto competition
        self.comp("Veto")
        NUM_VETO_PLAYERS = 6

        # updated veto competition section
        potential_players = list(set(self.houseguests) - set(nominees + [self.HOH]))

        if len(self.houseguests) > 3:
            veto_players = random.sample(
                potential_players,
                k=min(len(potential_players), NUM_VETO_PLAYERS - 3),
            )
            veto_players.extend(nominees + [self.HOH])
            self.veto_winner = random.choice(veto_players)
            self.print_text(f"{self.veto_winner} has won the Power of Veto!")

        else:
            self.veto_winner = None

        return potential_players

    def veto_ceremony(self, nominees, potential_players):
        if self.veto_winner is not None:
            self.veto_holder_label.setText(f"Veto Holder: {self.veto_winner.name}")
            # If veto winner is also a nominee, force them to use it on self
            if self.veto_winner in nominees:
                self.print_text(
                    f"{self.veto_winner.name} has automatically used the Veto on themselves."
                )
                nominee_saved = self.veto_winner
                nominee_saved.vetoed = True
                nominees.remove(nominee_saved)

            else:
                veto_used = random.choice([True, False])

                if veto_used:
                    nominee_saved = random.choice(nominees)

                    if nominee_saved == self.veto_winner:
                        self.print_text(
                            f"{self.veto_winner} has chosen to use the Power of Veto on themselves."
                        )
                    else:
                        self.print_text(
                            f"{self.veto_winner} has chosen to use the Power of Veto on {nominee_saved.name}."
                        )

                    nominees.remove(nominee_saved)
                    nominee_saved.vetoed = True

                    # Replacement nominations
                    if (
                        self.veto_winner.target
                        and self.veto_winner.target in potential_players
                        and not self.veto_winner.target.vetoed
                    ):
                        replacement_nom = next(
                            hg
                            for hg in potential_players
                            if hg.name == self.veto_winner.target and not hg.vetoed
                        )

                    elif potential_players:
                        replacement_nom = random.choice(potential_players)
                        while replacement_nom == nominee_saved:
                            replacement_nom = random.choice(potential_players)

                    nominees.append(replacement_nom)
                    self.print_text(
                        f"{self.HOH.name} has nominated {replacement_nom.name} as the replacement nominee."
                    )

                    self.replacement_nominees_label.setText(
                        f"R.NOMS: {', '.join([nom.name for nom in nominees])}"
                    )

                else:
                    self.print_text(
                        f"{self.veto_winner} has chosen not to use the Power of Veto."
                    )
                    self.replacement_nominees_label.setText(f"The veto was not used.")

        else:
            self.veto_holder_label.setText("The Veto is not played this week.")
            self.replacement_nominees_label.setText(
                "Nominees cannot be replaced this week."
            )

    def eviction(self, nominees):
        # Eviction
        votes = {}
        for houseguest in set(self.houseguests) - set([self.HOH]):
            # Calculate the average impression of each nominee
            nominee_impressions = {}
            for nom in nominees:
                nominee_impressions[nom] = sum(
                    hg.impressions[nom.name]
                    for hg in self.houseguests
                    if nom.name in hg.impressions
                ) / len(self.houseguests)

            # Vote for the nominee with the lower average impression
            vote = min(nominee_impressions, key=nominee_impressions.get)
            votes[houseguest.name] = vote.name

        evicted_name = max(votes, key=list(votes.values()).count)
        evicted = next(hg for hg in self.houseguests if hg.name == evicted_name)
        self.print_text(f"{evicted.name} has been evicted from the Big Brother house.")
        self.evicted_houseguests.append(evicted)
        self.houseguests.remove(evicted)
        # Update evicted houseguest
        self.evicted_label.setText(f"Evicted: {evicted.name}")

        # Update targets after eviction
        for hg in self.houseguests:
            if hg.target == evicted.name:
                hg.target = None

        # Remove evicted houseguest from the list
        row = None
        for i in range(self.houseguest_list.count()):
            if self.houseguest_list.item(i).text() == evicted.name:
                row = i
        if row is not None:
            self.houseguest_list.takeItem(row)

        # Reset "vetoed" status
        for hg in self.houseguests:
            hg.vetoed = False

    # RESET ========================================
    def reset(self):
        self.houseguests = []
        self.houseguest_list.clear()
        self.evicted_houseguests = []
        self.prev_HOH = None
        self.matrix = None
        self.end_state = 0  # Add this line

        # Clear all labels
        self.clear_labels()

        # Clear houseguest list
        self.houseguest_list.clear()

        # Repopulate houseguests and list
        self.create_players()
        for hg in self.houseguests:
            self.houseguest_list.addItem(hg.name)
        for h in self.houseguests:
            h.impressions = {}
        self.do_impressions()

        # Reset button text
        self.next_week_btn.setText("Continue")

    def clear_labels(self):
        # Clear all labels
        self.hoh_label.setText("")
        self.nominees_label.setText("")
        self.veto_holder_label.setText("")
        self.replacement_nominees_label.setText("")
        self.evicted_label.setText("")

    def show_preferences(self):
        
        # func for toggling the custom speed
        def toggle_custom_speed(self):
            index = print_speed_presets.currentIndex()
            if index == 3: 
                print_speed_custom.setDisabled(False)
            else:
                print_speed_custom.setDisabled(True)
                if index == 0:
                    print_speed_custom.setValue(0) # Reset value 
                elif index == 1:
                    print_speed_custom.setValue(0.2) # Reset value 
                elif index == 2:
                    print_speed_custom.setValue(0.8) # Reset value 
                    
        dialog = QDialog(self)
        layout = QVBoxLayout(dialog)
        self.retain_season = self.settings.value("RetainSeason", False)

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
            
    def update_print_speed(self, index, csp):
        if index == 0: # Slow
            self.print_speed = 0.8 
        elif index == 1: # Fast
            self.print_speed = 0.2
        elif index == 2: # Instant
            self.print_speed = 0
        else:
            self.print_speed = csp

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
                    alliance = random.sample(
                        self.houseguests, min(len(self.houseguests), 3)
                    )

                    self.event_3(hg1, hg2, alliance)
                else:
                    hg1, hg2 = random.sample(self.houseguests, 2)
                    self.event_4(hg1, hg2)

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

    def event_3(self, hg1, hg2, alliance):
        if hg2 not in alliance and hg1 not in alliance:
            for member in alliance:
                if member.loyalty > hg1.manipulativeness:
                    member.target = hg2.name
                    member.impressions[hg2.name] = max(
                        0, member.impressions[hg2.name] - 2
                    )
                    self.print_text(f"{member.name} was swayed!")

        alliance_name = "The " + random.choice(
            ["Wolves", "Dragons", "Lions", "Snakes", "Eagles"]
        )
        self.print_text(
            f"{hg1.name} makes plans with {alliance_name} to evict {hg2.name}."
        )

    def event_4(self, hg1, hg2):
        # Opinion changes
        hg1.impressions[hg2.name] = min(10, hg1.impressions[hg2.name] + 3)
        hg2.impressions[hg1.name] = min(10, hg2.impressions[hg1.name] + 3)
        self.print_text(f"{hg1.name} has a casual conversation with {hg2.name}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BigBrother()
    sys.exit(app.exec_())

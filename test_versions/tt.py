# Last updated 2/3/2024

import random
import re
import sys

import names
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPalette, QTextCursor
from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QPushButton, QSizePolicy, QTextEdit,
                             QVBoxLayout, QWidget)

NUM_PLAYERS = 12
PROFESSIONS = [
    "Accountant",
    "Actor",
    "Athlete",
    "Author",
    "Chef",
    "Engineer",
    "Entrepreneur",
    "Nurse",
    "Photographer",
    "Scientist",
    "Teacher",
]
MAX_EVENTS = 1


class HouseGuest:

    def __init__(self, name):
        # Generate random age and profession
        self.age = random.randint(21, 40)
        self.professions = PROFESSIONS
        self.profession = random.choice(self.professions)

        self.name = name
        self.HOH = False
        self.nominee = False
        self.veto = False
        self.target = None
        self.impressions = {}
        self.vetoed = False

        self.friendliness = random.randint(1, 5)
        self.loyalty = random.randint(1, 5)
        self.manipulativeness = random.randint(1, 5)
        self.emotionality = random.randint(1, 5)
        self.competitiveness = random.randint(1, 5)

    def __repr__(self):
        return self.name

    def summary(self):
        """Return a string with the houseguest's info"""
        return f"{self.name} - {self.age}, {self.profession}"


class Alliance:
    def __init__(self, members):
        self.members = members
        
        # Generate a random alliance name based on member names
        name_parts = [m.name for m in members]
        self.name = '_'.join(name_parts) + '_' + str(random.randint(0, 100))
        
    def get_members(self):
        return self.members
    
    def get_name(self):
        return self.name


class BigBrother(QWidget):

    def __init__(self):
        super().__init__()
        self.pending_updates = []  # Initialize an empty list to store pending updates
        self.current_update = None  # Keep track of the currently running update
        self.num_players = NUM_PLAYERS
        self.houseguests = []
        self.evicted_houseguests = []
        self.prev_HOH = None
        self.end_state = 0
        self.HOH = None
        self.nominees = None
        self.veto_winner = None
        self.evicted = None
        self.events = []  # Initialize a list to store events
        self.alliances = {}  # Initialize a dictionary to store alliances
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

        # Set layout
        overall = QVBoxLayout()
        layout = QHBoxLayout()

        # Create widget for left side
        self.left_widget = QWidget()

        # Set fixed size
        self.left_widget.setFixedSize(250, 400)

        # Layout for labels on left
        self.left_layout = QVBoxLayout()

        self.hoh_label = QLabel("HOH: ")
        self.nominees_label = QLabel("NOMS: ")

        """ self.next_week_btn = QPushButton("Continue")
        self.next_week_btn.clicked.connect(self.play_week) """

        # Add "Impressions" button
        self.impressions_btn = QPushButton("Impressions")
        self.impressions_btn.clicked.connect(self.show_impressions)

        self.left_layout = QVBoxLayout()
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

        self.setStyleSheet(
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

        self.setPalette(dark_palette)
        self.show()

    # Print text to box instead of console
    def print_text(self, text, nl=True):
        if nl:
            text += "\n"

        def update_text():
            cursor = self.text_box.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_box.setTextCursor(cursor)
            self.text_box.insertPlainText(text)

            # Apply formatting
            self.format_text()
            # Add more color_words calls for other keywords and names

            self.current_update = None  # Mark the current update as complete
            if self.pending_updates:  # If there are more pending updates
                update = self.pending_updates.pop(0)  # Get the next update
                QTimer.singleShot(300, update)  # Schedule it to run after a delay

        if not self.current_update:  # If there's no update currently running
            self.current_update = update_text  # Set the current update
            QTimer.singleShot(300, update_text)  # Schedule it to run after a delay
            if self.pending_updates:  # If there are more pending updates
                self.pending_updates.pop(0)  # Remove the current update from the queue
        else:
            self.pending_updates.append(update_text)  # Add this update to the queue

    def color_words(self, textedit, phrase, color):
        cursor = textedit.textCursor()
        text = textedit.toPlainText()
        phrase_len = len(phrase)
        start_index = 0
        while True:
            match = re.search(
                r"\b{}\b".format(phrase), text[start_index:], re.IGNORECASE
            )
            if not match:
                break
            start_index += match.start()
            cursor.setPosition(start_index)
            cursor.setPosition(start_index + phrase_len, QTextCursor.KeepAnchor)
            textedit.setTextCursor(cursor)
            textedit.setTextColor(color)
            start_index += phrase_len

    def format_text(self):
        # Apply custom formatting
        self.color_words(self.text_box, "HOH", Qt.yellow)
        self.color_words(self.text_box, "Head of Household", Qt.yellow)
        if self.HOH is not None:
            self.color_words(self.text_box, self.HOH.name, Qt.yellow)
        # Format entire sentence with houseguest name when swayed
        for hg in self.houseguests:
            phrase = r"\b{}\b\s+was swayed!".format(hg.name)
            self.color_words_phrase(self.text_box, phrase, Qt.magenta)

        # Format entire sentence with houseguest name when not buying it
        for hg in self.houseguests:
            phrase = r"But\s+\b{}\b\s+didn\'t buy it!".format(hg.name)
            self.color_words_phrase(self.text_box, phrase, Qt.magenta)

        if self.veto_winner:
            self.color_words(self.text_box, self.veto_winner.name, Qt.cyan)

        if self.nominees:
            for nominee in self.nominees:
                self.color_words(self.text_box, nominee.name, Qt.red)

    def color_words_phrase(self, textedit, phrase, color):
        cursor = textedit.textCursor()
        text = textedit.toPlainText()
        match = re.search(phrase, text, re.IGNORECASE)
        if match:
            start_index = match.start()
            end_index = match.end()
            cursor.setPosition(start_index)
            cursor.setPosition(end_index, QTextCursor.KeepAnchor)
            textedit.setTextCursor(cursor)
            textedit.setTextColor(color)

    def create_players(self):
        for i in range(self.num_players):
            name = names.get_first_name()
            self.houseguests.append(HouseGuest(name))

    def do_impressions(self):
        for hg1 in self.houseguests:
            for hg2 in self.houseguests:
                if hg1 != hg2:
                    impression = random.randint(0, 10)
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
        self.print_text(f"Week {self.week}:")

        if self.end_state == 1:
            self.close()

        # Check if only 2 players left
        # If more than 2 players, play regular week
        if len(self.houseguests) > 2:
            # Regular game play
            self.select_HOH()
            self.event_spawner()
            self.select_noms()
            self.event_spawner()
            pp = self.play_veto()
            self.event_spawner()
            self.veto_ceremony(pp)
            self.event_spawner()
            self.eviction()
            self.event_spawner()

        else:
            # Finale
            self.print_text(
                f"Final 2: {self.houseguests[0].name} and {self.houseguests[1].name}"
            )

            # Have them plead their case
            self.print_text(f"{self.houseguests[0].name} pleads their case...")
            self.print_text(f"{self.houseguests[1].name} pleads their case...")

            # Evicted houseguests vote
            votes = {}
            for guest in self.evicted_houseguests:
                votes[guest.name] = random.choice(self.houseguests).name

            votes1, votes2 = 0, 0
            for value in votes.keys():
                self.print_text(f"{value} votes for {votes[value]} to win Big Brother!")
                if votes[value] == self.houseguests[0].name:
                    votes1 += 1
                elif votes[value] == self.houseguests[1].name:
                    votes2 += 1

            if votes1 > votes2:
                winner = self.houseguests[0]
            elif votes2 > votes1:
                winner = self.houseguests[1]
            else:
                winner = random.choice(self.houseguests)

            self.print_text(f"{winner} wins Big Brother!")
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
            # TODO: Change noms text to votes for winner
            # TODO: Change veto text to votes for runner-up
            # TODO: Change r.noms text to AFP
            self.evicted_label.setText("Thanks for watching!")

            # Change button text
            self.next_week_btn.setText("Finish")
            self.end_state = 1

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

        if len(self.nominees) < 2:

            potential_nominees = list(
                set(self.houseguests) - set([self.HOH]) - set(self.nominees)
            )
            if potential_nominees:
                if self.HOH.target and self.HOH.target not in self.houseguests:
                    self.nominees.append(random.choice(potential_nominees))
                else:
                    self.nominees.append(random.choice(potential_nominees))

                potential_nominees.remove(self.nominees[-1])
                if potential_nominees:
                    self.nominees.append(random.choice(potential_nominees))

        for nominee in self.nominees:
            nominee.nominee = True

        self.print_text(
            f"{self.HOH.name} has nominated {self.nominees[0].name} and {self.nominees[1].name} for eviction."
        )
        self.nominees_label.setText(
            f"NOMS: {', '.join([nom.name for nom in self.nominees])}"
        )

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

    def veto_ceremony(self, potential_players):
        if self.veto_winner is not None:
            self.veto_holder_label.setText(f"Veto Holder: {self.veto_winner.name}")
            # If veto winner is also a nominee, force them to use it on self
            if self.veto_winner in self.nominees:
                self.print_text(
                    f"{self.veto_winner.name} has automatically used the Veto on themselves."
                )
                nominee_saved = self.veto_winner
                nominee_saved.vetoed = True
                self.nominees.remove(nominee_saved)

            else:
                veto_used = random.choice([True, False])

                if veto_used:
                    nominee_saved = random.choice(self.nominees)

                    if nominee_saved == self.veto_winner:
                        self.print_text(
                            f"{self.veto_winner} has chosen to use the Power of Veto on themselves."
                        )
                    else:
                        self.print_text(
                            f"{self.veto_winner} has chosen to use the Power of Veto on {nominee_saved.name}."
                        )

                    self.nominees.remove(nominee_saved)
                    nominee_saved.vetoed = True

                    # Replacement nominations
                    if (
                        self.veto_winner is not None
                        and self.veto_winner.target
                        and self.veto_winner.target in self.houseguests
                    ):
                        replacement_nom = next(
                            hg
                            for hg in self.houseguests
                            if hg.name == self.veto_winner.target and hg.vetoed is False
                        )

                    elif (
                        self.veto_winner is not None
                        and self.veto_winner.target not in potential_players
                    ):
                        replacement_nom = random.choice(potential_players)
                        while replacement_nom == nominee_saved:
                            replacement_nom = random.choice(potential_players)

                    self.nominees.append(replacement_nom)
                    self.print_text(
                        f"{self.HOH.name} has nominated {replacement_nom.name} as the replacement nominee."
                    )

                    if len(self.nominees) == 2:
                        self.replacement_nominees_label.setText(
                            f"R.NOMS: {', '.join([nom.name for nom in self.nominees])}"
                        )
                    elif len(self.nominees) == 1:
                        self.replacement_nominees_label.setText(
                            f"R.NOM: {self.nominees[0].name}"
                        )
                    else:
                        self.replacement_nominees_label.setText(
                            "The veto was not used."
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

    def eviction(self):
        # Eviction
        votes = {}
        for houseguest in set(self.houseguests) - set([self.HOH]):
            votes[houseguest.name] = random.choice(self.nominees).name
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
                    a_members = [x for x in self.houseguests if x not in [hg2]]
                    alliance = random.sample(a_members, random.randint(2, 4))
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
        self.print_text(f"{hg1.name} pulls {hg2.name} aside to talk about {hg3.name}.")

        if hg1.manipulativeness >= random.randint(0, hg2.emotionality):
            hg2.target = hg3.name
            self.print_text(f"{hg2.name} was swayed!")

            # Opinion changes
            if hg1.impressions[hg3.name] >= 5:
                hg1.impressions[hg3.name] += 1
                hg2.impressions[hg3.name] += 2
            else:
                hg1.impressions[hg3.name] -= 1
                hg2.impressions[hg3.name] -= 2

        else:
            self.print_text(f"But {hg2.name} didn't buy it!")

            # Opinion changes
            hg1.impressions[hg2.name] -= 1
            hg2.impressions[hg1.name] -= 1

    def event_2(self, hg1, hg2):
        topic = random.choice(
            [
                "the dishes",
                "who ate the last slice of pizza",
                "who flirts too much",
                "who snores",
            ]
        )
        self.print_text(f"{hg1.name} gets in a fight with {hg2.name} over {topic}!")

        if hg1.friendliness < hg2.emotionality:
            hg1.target = hg2.name
            hg2.target = hg1.name

        # Opinion changes
        if random.random() < 0.8:
            hg1.impressions[hg2.name] = max(0, hg1.impressions[hg2.name] - 3)
            hg2.impressions[hg1.name] = max(0, hg2.impressions[hg1.name] - 3)

    def event_3(self, hg1, hg2, alliance):
        alliance_name = "The " + random.choice(
            ["Wolves", "Dragons", "Lions", "Snakes", "Eagles"]
        )

        self.print_text(
            f"{hg1.name} makes plans with {alliance_name} to evict {hg2.name}."
        )

        if hg2 not in alliance and hg1 not in alliance:
            for member in alliance:
                if member.loyalty > hg1.manipulativeness:
                    member.target = hg2.name
                    member.impressions[hg2.name] = max(
                        0, member.impressions[hg2.name] - 2
                    )
                    self.print_text(f"{member.name} was swayed!")

    def event_4(self, hg1, hg2):
        self.print_text(f"{hg1.name} has a pleasant conversation with {hg2.name}.")
        hg1.impressions[hg2.name] = min(10, hg1.impressions[hg2.name] + 3)
        hg2.impressions[hg1.name] = min(10, hg2.impressions[hg1.name] + 3)

    def event_5(self, hg1, hg2):
        alliance = Alliance([hg1, hg2])
        self.print_text(f"{hg1.name} created an alliance with {hg2.name} called {alliance.name}.")
        if hg1.impressions[hg2.name] >= 5 and hg2.impressions[hg1.name] >= 5:
            hg1.impressions[hg2.name] += 3
            hg2.impressions[hg1.name] += 3
        elif hg1.impressions[hg2.name] < 5 and hg2.impressions[hg1.name] >= 5:
            self.print_text(f"But {hg1.name} doesn't plan to stick to it...")
            hg1.impressions[hg2.name] -= 1
            hg2.impressions[hg1.name] += 3
        elif hg1.impressions[hg2.name] >= 5 and hg2.impressions[hg1.name] < 5:
            self.print_text(f"But {hg2.name} doesn't plan to stick to it...")
            hg1.impressions[hg2.name] += 3
            hg2.impressions[hg1.name] -= 1
        else:
            self.print_text(f"But it appears to be all for show...")
            hg1.impressions[hg2.name] -= 1
            hg2.impressions[hg1.name] -= 1
        self.alliances.append(alliance)


class EditNameDialog(QDialog):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Name")

        # Layout
        layout = QVBoxLayout(self)

        # Name input
        self.name_input = QLineEdit(name)
        layout.addWidget(self.name_input)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self):
        return self.name_input.text()


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BigBrother()
    sys.exit(app.exec_())

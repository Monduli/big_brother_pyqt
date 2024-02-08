# Last updated 2/3/2024

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QTextEdit,
    QSizePolicy,
    QGridLayout
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QTimer
import random
import names

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


class Event:
    def __init__(self):
        pass

    def event_1(self, hg1, hg2, hg3):
        if hg1.manipulativeness >= random.randint(0, hg2.emotionality):
            hg2.target = hg3.name

        # Opinion changes
        if hg1.impressions[hg3.name] >= 5:
            hg1.impressions[hg3.name] = min(10, hg1.impressions[hg3.name] + 1)
            hg2.impressions[hg3.name] = max(0, min(10, hg2.impressions[hg3.name] + 2))
        else:
            hg1.impressions[hg3.name] = max(0, hg1.impressions[hg3.name] - 1)
            hg2.impressions[hg3.name] = max(0, hg2.impressions[hg3.name] - 2)

    def event_2(self, hg1, hg2):
        if hg1.friendliness < hg2.emotionality:
            hg1.target = hg2.name
            hg2.target = hg1.name

        # Opinion changes
        if random.random() < 0.8:
            hg1.impressions[hg2.name] = max(0, hg1.impressions[hg2.name] - 3)
            hg2.impressions[hg1.name] = max(0, hg2.impressions[hg1.name] - 3)

    def event_3(self, hg1, hg2, alliance):
        if hg2 not in alliance and hg1 not in alliance:
            for member in alliance:
                if member.loyalty > hg1.manipulativeness:
                    member.target = hg2.name
                    member.impressions[hg2.name] = max(0, member.impressions[hg2.name] - 2)

    def event_4(self, hg1, hg2):
        # Opinion changes
        hg1.impressions[hg2.name] = min(10, hg1.impressions[hg2.name] + 3)
        hg2.impressions[hg1.name] = min(10, hg2.impressions[hg1.name] + 3)


class BigBrother(QWidget):

    def __init__(self):
        super().__init__()
        self.num_players = NUM_PLAYERS
        self.houseguests = []
        self.evicted_houseguests = []
        self.prev_HOH = None
        self.end_state = 0
        self.event = Event()
        self.events = []  # Initialize a list to store events
        self.alliances = {}  # Initialize a dictionary to store alliances
        self.create_players()
        self.do_impressions()
        self.initUI()
        self.introduce_players()
        self.matrix = ImpressionMatrix(self.houseguests)

    def initUI(self):
        # Create the QListWidget and add all houseguests
        self.list_items = []
        self.houseguest_list = QListWidget()
        for hg in self.houseguests:
            self.houseguest_list.addItem(hg.name)
            self.list_items.append(hg.name)

        # Set layout
        overall = QVBoxLayout()
        layout = QHBoxLayout()

        # Create widget for left side
        self.left_widget = QWidget()

        # Set fixed size
        self.left_widget.setFixedSize(250, 400)

        # Layout for labels on left
        self.left_layout = QVBoxLayout()

        self.hoh_label = QLabel("Head of Household: ")
        self.nominees_label = QLabel("Nominees: ")

        """ self.next_week_btn = QPushButton("Continue")
        self.next_week_btn.clicked.connect(self.play_week) """

        # Add "Impressions" button
        self.impressions_btn = QPushButton("Impressions")
        self.impressions_btn.clicked.connect(self.show_impressions)

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.hoh_label)
        self.left_layout.addWidget(self.nominees_label)
        # Add veto holder label
        self.veto_holder_label = QLabel("Veto Holder: ")

        # Add replacement nominees label
        self.replacement_nominees_label = QLabel("Replacement Nominees: ")

        # Add evicted houseguest label
        self.evicted_label = QLabel("Evicted: ")

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
    def print_text(self, text):
        self.text_box.append(text + '\n')
        # Pause for 300 milliseconds
        QTimer.singleShot(300, lambda: None)

    def show_impressions(self):
        self.matrix.appear(self.houseguests)

    def create_players(self):
        for i in range(self.num_players):
            name = names.get_first_name()
            self.houseguests.append(HouseGuest(name))

    def do_impressions(self):
        for hg1 in self.houseguests:
            for hg2 in self.houseguests:
                if hg1 != hg2:
                    impression = random.randint(0,10)
                    hg1.impressions[hg2.name] = impression
        for hg in self.houseguests:
            print(hg.name, hg.impressions)

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
        if len(self.houseguests) == 2:

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
            self.hoh_label.setText(f"Winner: {winner.name}")

            # Change button text
            self.next_week_btn.setText("Finish")
            self.end_state = 1

        else:
            # Regular game play
            # Call the event spawner to generate random events
            self.event_spawner()

            # Choose HOH
            # Check if only 3 players left
            if len(self.houseguests) > 3:

                # Can't be HOH two weeks in a row
                potential_HOHs = [hg for hg in self.houseguests if hg != self.prev_HOH]

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

            # Call the event spawner to generate random events
            self.event_spawner()

            # Nominate two players
            nominees = []

            worst_impressions = [
                (name, impression) 
                for name, impression in sorted(self.HOH.impressions.items(), key=lambda x: x[1])[:2]
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

            # Call the event spawner to generate random events
            self.event_spawner()

            # Play veto competition
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

            # Call the event spawner to generate random events
            self.event_spawner()

            # Veto ceremony
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
                            self.veto_winner is not None
                            and self.veto_winner.target
                            and self.veto_winner.target in self.houseguests
                        ):
                            replacement_nom = next(
                                hg
                                for hg in self.houseguests
                                if hg.name == self.veto_winner.target
                                and hg.vetoed == False
                            )

                        elif (
                            self.veto_winner is not None
                            and self.veto_winner.target not in potential_players
                        ):
                            replacement_nom = random.choice(potential_players)
                            while replacement_nom == nominee_saved:
                                replacement_nom = random.choice(potential_players)

                        nominees.append(replacement_nom)
                        self.print_text(
                            f"{self.HOH.name} has nominated {replacement_nom.name} as the replacement nominee."
                        )

                        if len(nominees) == 2:
                            self.replacement_nominees_label.setText(
                                f"Replacement Nominees: {', '.join([nom.name for nom in nominees])}"
                            )
                        elif len(nominees) == 1:
                            self.replacement_nominees_label.setText(
                                f"Replacement Nominee: {nominees[0].name}"
                            )
                        else:
                            self.replacement_nominees_label.setText(
                                "The veto was not used."
                            )

                    else:
                        self.print_text(
                            f"{self.veto_winner} has chosen not to use the Power of Veto."
                        )
                        self.replacement_nominees_label.setText(
                            f"The veto was not used."
                        )

            else:
                self.veto_holder_label.setText("The Veto is not played this week.")
                self.replacement_nominees_label.setText(
                    f"Nominees cannot be replaced this week."
                )

            # Call the event spawner to generate random events
            self.event_spawner()
            
            # Eviction
            votes = {}
            for houseguest in set(self.houseguests) - set([self.HOH]):
                votes[houseguest.name] = random.choice(nominees).name
            evicted_name = max(votes, key=list(votes.values()).count)
            evicted = next(hg for hg in self.houseguests if hg.name == evicted_name)
            self.print_text(
                f"{evicted.name} has been evicted from the Big Brother house."
            )
            self.evicted_houseguests.append(evicted)
            self.houseguests.remove(evicted)
            # Update evicted houseguest
            self.evicted_label.setText(f"Evicted: {evicted.name}")

            # Update targets after eviction
            for hg in self.houseguests:
                if hg.target == evicted.name:
                    hg.target = None

            # Update the HOH and nominees labels
            self.hoh_label.setText(f"Head of Household: {self.HOH.name}")
            self.nominees_label.setText(
                f"Nominees: {', '.join([nom.name for nom in nominees])}"
            )

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

    # Reset game
    def reset(self):
        self.houseguests = []
        self.evicted_houseguests = []
        self.prev_HOH = None

        # Clear all labels
        self.hoh_label.setText("")
        self.nominees_label.setText("")
        # etc

        # Clear houseguest list
        self.houseguest_list.clear()

        # Repopulate houseguests and list
        self.create_players()
        for hg in self.houseguests:
            self.houseguest_list.addItem(hg.name)

        # Reset button text
        self.next_week_btn.setText("Continue")

    def event_spawner(self):
        # Add random events
        for _ in range(random.randint(0, MAX_EVENTS)):
            event_index = random.randint(0, 3)
            if event_index == 0:
                hg1, hg2, hg3 = random.sample(self.houseguests, 3)
                self.event.event_1(hg1, hg2, hg3)
                self.print_text(f"{hg1.name} pulls {hg2.name} aside to talk about {hg3.name}.")
            elif event_index == 1:
                hg1, hg2 = random.sample(self.houseguests, 2)
                topic = random.choice(["the dishes", "who ate the last slice of pizza", "who flirts too much", "who snores"])
                self.event.event_2(hg1, hg2)
                self.print_text(f"{hg1.name} gets in a fight with {hg2.name} over {topic}!")
            elif event_index == 2:
                hg1, hg2 = random.sample(self.houseguests, 2)
                alliance_name = "The " + random.choice(["Wolves", "Dragons", "Lions", "Snakes", "Eagles"])
                alliance = random.sample(self.houseguests, random.randint(2, 4))
                self.alliances[alliance_name] = alliance
                self.event.event_3(hg1, hg2, alliance)
                self.print_text(f"{hg1.name} makes plans with {alliance_name} to evict {hg2.name}.")
            else:
                hg1, hg2 = random.sample(self.houseguests, 2)
                self.event.event_4(hg1, hg2)
                self.print_text(f"{hg1.name} has a casual conversation with {hg2.name}.")

class ImpressionMatrix(QWidget):
    def __init__(self, houseguests):
        super().__init__()
        self.houseguests = houseguests
        self.impressions = {}
        for hg in houseguests:
            self.impressions[hg.name] = hg.impressions.copy()
        #print(self.impressions)
        self.init_matrix()
        self.setStyleSheet("""
            QLabel {
                font-size: 20px; 
            }
            """)

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
        for col in range(1, num_hgs+1):
            grid.setColumnStretch(col, 1)
            grid.setColumnMinimumWidth(col, 75)
        for row in range(1, num_hgs+1):
            grid.setRowStretch(row, 1)
            grid.setRowMinimumHeight(row, 75)

        # Add names along top row and left column
        for col, hg in enumerate(self.houseguests):
            name = QLabel(hg.name)
            name.setAlignment(Qt.AlignCenter)
            grid.addWidget(name, 0, col+1)
            
        for row, hg in enumerate(self.houseguests):
            name = QLabel(hg.name)
            name.setAlignment(Qt.AlignCenter)
            grid.addWidget(name, row+1, 0)
            
        # Add impression values to grid    
        for row, hg1 in enumerate(self.houseguests):
            for col, hg2 in enumerate(self.houseguests):
                if hg1 != hg2:
                    value = QLabel(str(self.impressions[hg1.name][hg2.name]))   
                else:
                    value = QLabel(str("X"))   
                value.setAlignment(Qt.AlignCenter)
                grid.addWidget(value, row+1, col+1)

    def appear(self, houseguests):
        self.impressions = {}
        for hg in houseguests:
            self.impressions[hg.name] = hg.impressions.copy()
        #print(self.impressions)
        self.init_matrix()
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BigBrother()
    sys.exit(app.exec_())

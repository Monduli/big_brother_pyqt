import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget
from PyQt5.QtCore import Qt
import random 
import names

NUM_PLAYERS = 12
PROFESSIONS = ["Accountant", "Actor", "Athlete", "Author", 
                "Chef", "Engineer", "Entrepreneur", "Nurse", 
                "Photographer", "Scientist", "Teacher"]

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

    def __repr__(self):
        return self.name
    
    def summary(self):
        """Return a string with the houseguest's info""" 
        return f"{self.name} - {self.age}, {self.profession}"

class BigBrother(QWidget):
    
    def __init__(self):
        super().__init__()
        self.num_players = NUM_PLAYERS
        self.houseguests = []
        self.evicted_houseguests = []
        self.prev_HOH = None
        self.end_state = 0
        self.create_players()
        self.introduce_players()
        self.initUI()
        
    def initUI(self):
        # Create the QListWidget and add all houseguests
        self.list_items = []
        self.houseguest_list = QListWidget()
        for hg in self.houseguests:
            self.houseguest_list.addItem(hg.name)
            self.list_items.append(hg.name)
        
        # Set layout
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

        layout.addLayout(right_layout)
        
        # Add Continue button 
        self.next_week_btn = QPushButton("Continue")
        self.next_week_btn.clicked.connect(self.play_week)

        # Add reset button 
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)

        layout.addWidget(self.reset_btn)
        layout.addWidget(self.next_week_btn , alignment=Qt.AlignBottom)

        self.setLayout(layout)
        self.show()
        
    def create_players(self):
        for i in range(self.num_players):
            name = names.get_first_name()
            self.houseguests.append(HouseGuest(name))
        
    def introduce_players(self):
        print(f"Meet the {len(self.houseguests)} houseguests:")
        for player in self.houseguests:
            print(player.summary()) 
            
    def play_week(self):
        """Simulate a week of Big Brother"""
        self.week = self.num_players - len(self.houseguests)+1
        print(f"Week {self.week}:")

        if self.end_state == 1:
            self.close()

        # Check if only 2 players left
        if len(self.houseguests) == 2:

            # Finale
            print(f"Final 2: {self.houseguests[0].name} and {self.houseguests[1].name}")

            # Have them plead their case
            print(f"{self.houseguests[0].name} pleads their case...")  
            print(f"{self.houseguests[1].name} pleads their case...")

            # Evicted houseguests vote
            votes = {}  
            for guest in self.evicted_houseguests:
                votes[guest.name] = random.choice(self.houseguests).name

            votes1, votes2 = 0, 0
            for value in votes.keys():
                print(f"{value} votes for {votes[value]} to win Big Brother!")
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

            print(f"{winner} wins Big Brother!")
            # Clear all labels except first
            for i in range(1, self.left_layout.count()):  
                self.left_layout.itemAt(i).widget().setText("")
            # Remove evicted houseguest from the list
            for i in range(self.houseguest_list.count()):
                print(self.houseguest_list.item(i).text())
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
        
            #Choose HOH
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
            print(f"{self.HOH.name} is the new Head of Household")
            
            #Nominate two players
            nominees = random.sample(list(set(self.houseguests) - set([self.HOH])), 2)  
            for nominee in nominees:
                nominee.nominee = True
            print(f"{self.HOH.name} has nominated {nominees[0].name} and {nominees[1].name} for eviction.")   
            
            #Play veto competition
            NUM_VETO_PLAYERS = 6

            # updated veto competition section
            potential_players = list(set(self.houseguests) - set(nominees + [self.HOH]))
                    
            if len(self.houseguests) > 3:
                veto_players = random.sample(potential_players, k=min(len(potential_players), NUM_VETO_PLAYERS-3))
                veto_players.extend(nominees + [self.HOH])
                self.veto_winner = random.choice(veto_players)
                print(f"{self.veto_winner} has won the Power of Veto!")
                
            else:
                self.veto_winner = None
            
            # Veto ceremony
            if self.veto_winner is not None:
                self.veto_holder_label.setText(f"Veto Holder: {self.veto_winner.name}")
                # If veto winner is also a nominee, force them to use it on self
                if self.veto_winner in nominees:
                    print(f"{self.veto_winner.name} has automatically used the Veto on themselves.")
                    nominee_saved = self.veto_winner
                    nominees.remove(nominee_saved)
                
                else:
                    veto_used = random.choice([True, False])

                    if veto_used:
                        nominee_saved = random.choice(nominees)
                    
                        if nominee_saved == self.veto_winner:
                            print(f"{self.veto_winner} has chosen to use the Power of Veto on themselves.")
                        else:
                            print(f"{self.veto_winner} has chosen to use the Power of Veto on {nominee_saved.name}.")
                            
                        nominees.remove(nominee_saved)
                        replacement_nom = random.choice(potential_players)
                        nominees.append(replacement_nom)
                        
                        print(f"{self.HOH.name} has nominated {replacement_nom.name} as the replacement nominee.")
                        if len(nominees) == 2:
                            self.replacement_nominees_label.setText(f"Replacement Nominees: {', '.join([nom.name for nom in nominees])}")
                        elif len(nominees) == 1:
                            self.replacement_nominees_label.setText(f"Replacement Nominee: {nominees[0].name}")
                        else:
                            self.replacement_nominees_label.setText("The veto was not used.")

                    else:
                        print(f"{self.veto_winner} has chosen not to use the Power of Veto.")
                        self.replacement_nominees_label.setText(f"The veto was not used.")
            
            else:
                self.veto_holder_label.setText("The Veto is not played this week.")
                self.replacement_nominees_label.setText(f"Nominees cannot be replaced this week.")

            #Eviction
            votes = {}
            for houseguest in set(self.houseguests) - set([self.HOH]):
                votes[houseguest.name] = random.choice(nominees).name
            evicted_name = max(votes, key=list(votes.values()).count)
            evicted = next(hg for hg in self.houseguests if hg.name == evicted_name)
            print(f"{evicted.name} has been evicted from the Big Brother house.")
            self.evicted_houseguests.append(evicted)
            self.houseguests.remove(evicted)
            # Update evicted houseguest
            self.evicted_label.setText(f"Evicted: {evicted.name}")
            
            # Update the HOH and nominees labels
            self.hoh_label.setText(f"Head of Household: {self.HOH.name}")
            self.nominees_label.setText(f"Nominees: {', '.join([nom.name for nom in nominees])}")

            # Remove evicted houseguest from the list
            for i in range(self.houseguest_list.count()):
                print(self.houseguest_list.item(i).text())
                if self.houseguest_list.item(i).text() == evicted.name:
                    row = i
            self.houseguest_list.takeItem(row)

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
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BigBrother()
    sys.exit(app.exec_())
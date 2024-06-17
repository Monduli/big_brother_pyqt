import random
import re

from alliance import Alliance
from bberror import BBError
from constants import *
from PyQt5.QtCore import QSettings, Qt, QTimer
from PyQt5.QtGui import QColor, QPalette, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Events:

    def __init__(self, big_brother):
        self.bb = big_brother
        self.added_info = None
        self.houseguests = self.bb.houseguests

    def event_spawner(self, ps=False):
        self.houseguests = self.bb.houseguests
        if len(self.houseguests) >= 2:
            try:
                self.bb.make_formatting()
                # Random events
                for _ in range(random.randint(0, MAX_EVENTS)):
                    potential_hgs = [
                        hg
                        for hg in self.houseguests
                        if hg not in self.bb.evicted_houseguests
                    ]

                    if ps:
                        pass
                        # pre season events

                    if len(potential_hgs) >= 3:
                        hg1, hg2, hg3 = random.sample(potential_hgs, 3)

                        event_index = random.randint(0, 20)
                        if event_index == 0 and len(self.houseguests) >= 3:
                            self.gossip(hg1, hg2, hg3)
                        elif event_index == 1:
                            self.get_in_fight(hg1, hg2)
                        elif (
                            event_index == 2
                            and len(self.houseguests) >= 4
                            and len(hg1.alliances) > 0
                        ):
                            self.alliance_target(hg1, hg2)
                        elif event_index == 3 and len(self.houseguests) >= 4:
                            self.form_alliance(hg1)
                        elif event_index == 4 and len(self.houseguests) >= 2:
                            self.showmance(hg1, hg2)
                        elif (
                            event_index == 5
                            and len(self.houseguests) >= 3
                            and len(hg1.alliances) > 0
                            and len(hg2.alliances) > 0
                        ):
                            self.alliance_betrayal(hg1, hg2, hg3)
                        elif event_index == 6 and len(hg1.alliances) > 0:
                            alliance = random.choice(list(self.bb.alliances.values()))
                            self.alliance_meeting(alliance)
                        elif event_index == 7 and len(self.houseguests) >= 2:
                            self.save_from_the_block(hg1, hg2)
                        elif event_index == 8 and len(self.houseguests) >= 2:
                            self.bond_over_interest(hg1, hg2)
                        else:
                            event = random.choice([self.casual_conversation, self.bond_over_hobby, self.discuss_favorites, self.reminisce, self.help_with_chores])
                            event(hg1,hg2)
                    else:
                        hg1, hg2 = random.sample(potential_hgs, 2)
                        self.casual_conversation(hg1, hg2)
            except Exception as e:
                raise BBError(e, self.bb, self.added_info) from e

    def comp(self, v):
        if v == "HOH":
            comp_name = random.choice(HOH_COMPS)[0]
            hoh_text = f"The houseguests compete in the {comp_name} HOH competition."
            self.bb.formatting[hoh_text] = self.bb.hoh_color
            self.bb.print_text(hoh_text)

            # Simulate the competition
            participants = [hg for hg in self.bb.houseguests if hg != self.bb.prev_HOH]
            random.shuffle(participants)
            winner = None

            for i in range(len(participants)):
                houseguest = participants[i]
                if i == len(participants) - 1:
                    winner = houseguest
                    self.bb.print_text(
                        f"{houseguest} wins the {comp_name} HOH competition!"
                    )
                else:
                    self.bb.print_text(
                        f"{houseguest} is out of the competition.", False
                    )

            return winner

        elif v == "Veto":
            comp_name = random.choice(VETO_COMPS)[0]
            veto_text = f"The houseguests compete in the {comp_name} veto competition."
            self.bb.formatting[veto_text] = self.bb.veto_color
            self.bb.print_text(veto_text)

            # Select participants for the veto competition
            participants = [self.bb.HOH] + self.bb.nominees
            remaining_houseguests = [
                hg for hg in self.bb.houseguests if hg not in participants
            ]
            num_random_players = 3
            houseguest_choice_drawn = False

            while len(participants) < 6 and len(remaining_houseguests) > 0:
                if not houseguest_choice_drawn and random.random() < 1 / (
                    len(self.bb.houseguests) - len(participants) + 1
                ):
                    chooser = random.choice(participants)
                    chosen_houseguest = max(
                        remaining_houseguests,
                        key=lambda hg: hg.impressions[chooser.name],
                    )
                    participants.append(chosen_houseguest)
                    remaining_houseguests.remove(chosen_houseguest)
                    self.bb.print_text(
                        f"{chooser} draws houseguest choice and selects {chosen_houseguest} to play in the veto competition."
                    )
                    houseguest_choice_drawn = True
                else:
                    random_player = random.choice(remaining_houseguests)
                    participants.append(random_player)
                    remaining_houseguests.remove(random_player)
                    self.bb.print_text(
                        f"{random_player} is randomly selected to play in the veto competition."
                    )

            # Simulate the competition
            random.shuffle(participants)
            winner = None

            for i in range(len(participants)):
                houseguest = participants[i]
                if i == len(participants) - 1:
                    winner = houseguest
                    self.bb.print_text(
                        f"{houseguest} wins the {comp_name} veto competition!"
                    )
                else:
                    self.bb.print_text(f"{houseguest} is out of the competition.")

            return winner

        else:
            return None

    def gossip(self, hg1, hg2, hg3):
        # Player pulls aside another player to tell them to target third player.
        # If succeeds, adds 2 to impressions for each hg other than the third who loses 2.

        self.bb.print_text(
            f"{hg1.name} pulls {hg2.name} aside to talk about {hg3.name}."
        )
        self.bb.print_text(
            f"{hg1.name}: You know, {hg2.name}, {hg3.name} is just no good..."
        )
        if hg1.manipulativeness >= random.randint(0, hg2.emotionality):
            hg2.target = hg3.name
            self.bb.print_text(f"{hg2.name} was swayed!")
            self.swayed_event(hg1, hg2)
            self.swayed_event(hg2, hg1)
            self.unswayed_event(hg2, hg3)
        else:
            self.bb.print_text(f"{hg2.name} was not swayed!")
            self.unswayed_event(hg1, hg2)
            self.unswayed_event(hg2, hg1)

    def get_in_fight(self, hg1, hg2):
        topic = self.get_fight_topic()
        self.bb.print_text(f"{hg1.name} gets in a fight with {hg2.name} over {topic}!")

        if hg1.friendliness > hg2.emotionality or hg2.friendliness > hg1.emotionality:
            self.bb.print_text(
                f"But their friendship is too strong! {hg1.name} and {hg2.name} made up!"
            )
        elif (
            hg1.friendliness == hg2.emotionality
            and hg2.friendliness == hg1.emotionality
        ):
            self.bb.print_text(
                f"In a rare move, {hg1.name} and {hg2.name} agree to disagree!"
            )
        else:
            hg1.target = hg2.name
            hg2.target = hg1.name
            self.unswayed_event(hg1, hg2, 3)
            self.unswayed_event(hg2, hg1, 3)
            self.bb.print_text(
                f"They're inconsolable! They both walk off in a huff after a screaming fit!"
            )

    def get_fight_topic(self):
        topic = random.choice(fight_topics)
        if "{food}" in topic:
            foods = [
                "slice of pizza",
                "slice of cake",
                "cookie",
                "sandwich",
                "piece of fruit",
                "bag of chips",
            ]
            topic = topic.replace("{food}", random.choice(foods))
        if "{drink}" in topic:
            drinks = [
                "bottle of wine",
                "beer",
                "soda",
                "juice",
                "cup of coffee",
                "glass of milk",
            ]
            topic = topic.replace("{drink}", random.choice(drinks))
        if "{item}" in topic:
            items = [
                "towel",
                "book",
                "magazine",
                "remote control",
                "dirty dish",
                "piece of clothing",
            ]
            topic = topic.replace("{item}", random.choice(items))
        if "{room}" in topic:
            rooms = ["kitchen", "living room", "bathroom", "bedroom"]
            topic = topic.replace("{room}", random.choice(rooms))
        if "{houseguest}" in topic:
            hgs = [hg.name for hg in self.houseguests]
            topic = topic.replace("{houseguest}", random.choice(hgs))
        return topic

    def alliance_target(self, hg1, hg2):
        # One houseguest (hg1) suggests an alliance go after another player (hg2).
        # Individually checks the members of the alliance.
        pick = None

        potential_alliances = []
        for alliance_name in hg1.alliances:
            alliance = self.bb.alliances[alliance_name]
            if hg2 not in alliance.members:
                potential_alliances.append(alliance)

        if potential_alliances:
            alliance = random.choice(potential_alliances)

        if pick != None:
            self.bb.print_text(
                f"{hg1.name} makes plans with {alliance.name} to target {hg2.name}."
            )

            for member in alliance.members:
                if member.name in self.houseguests:
                    if member.loyalty > hg1.manipulativeness:
                        member.target = hg2.name
                        self.swayed_event(member, hg1)
                        self.unswayed_event(member, hg2)
                        self.bb.print_text(f"{member.name} was convinced.")

    def casual_conversation(self, hg1, hg2):
        # Casual conversation. 100% chance of increasing impression by 1 or 2.
        self.bb.print_text(f"{hg1.name} has a casual conversation with {hg2.name}.")
        self.swayed_event(hg1, hg2)

    def form_alliance(self, hg1):
        alliance_size = random.randint(2, len(self.houseguests) // 2)
        alliance_members = random.sample(self.houseguests, alliance_size)

        alliance_name = self.generate_alliance_name(alliance_members)
        alliance = Alliance(alliance_name)

        for member in alliance_members:
            alliance.add_member(member)
            member.join_alliance(alliance)

        self.bb.alliances[alliance_name] = alliance

        self.bb.print_text(
            f"{alliance_name} alliance forms between {', '.join([member.name for member in alliance_members])}."
        )

    def showmance(self, hg1, hg2):
        # Two houseguests (hg1 and hg2) develop a romantic relationship, or "showmance".
        self.bb.print_text(f"{hg1.name} and {hg2.name} have developed a showmance!")
        self.swayed_event(hg1, hg2, 3)
        self.swayed_event(hg2, hg1, 3)
        self.bb.print_text(f"The two lovebirds are now inseparable!")

        # Add the showmance to the list
        self.bb.showmances.append((hg1, hg2))

    def alliance_betrayal(self, hg1, hg2, hg3):
        # One houseguest (hg1) betrays their alliance member (hg2) by telling another player (hg3) to target them.
        self.bb.print_text(
            f"{hg1.name} betrays their alliance member {hg2.name} by telling {hg3.name} to target them."
        )
        if hg1.manipulativeness >= random.randint(0, hg3.emotionality):
            hg3.target = hg2.name
            self.swayed_event(hg1, hg3)
            self.unswayed_event(hg1, hg2)
            self.bb.print_text(f"{hg3.name} was convinced to target {hg2.name}.")
        else:
            self.unswayed_event(hg1, hg3)
            self.bb.print_text(f"{hg3.name} was not convinced to target {hg2.name}.")

    def alliance_meeting(self, alliance):
        self.bb.print_text(
            f"The {alliance.name} alliance holds a meeting to discuss their strategy."
        )
        for member in alliance.members:
            if member in self.houseguests:
                other_member = random.choice(
                    [m for m in alliance.members if m != member]
                )
                self.swayed_event(member, other_member)

    def save_from_the_block(self, hg1, hg2):
        shared_alliances = list(set(hg1.alliances) & set(hg2.alliances))
        if shared_alliances:
            alliance = random.choice(shared_alliances)
            self.bb.print_text(
                f"{hg1.name} saves {hg2.name} from eviction, strengthening their bond within the {alliance} alliance."
            )
            self.swayed_event(hg1, hg2, 3)
            self.swayed_event(hg2, hg1, 3)
            
    ##### Non-Move Events
    # Aka: Events that do not involve making large changes in the game.

    def bond_over_interest(self, hg1, hg2):
        interests = ["cooking", "music", "sports", "movies", "fashion"]
        shared_interest = random.choice(interests)
        self.bb.print_text(
            f"{hg1.name} and {hg2.name} bond over their shared interest in {shared_interest}."
        )
        self.swayed_event(hg1, hg2, 2)
        self.swayed_event(hg2, hg1, 2)
        
    def share_stories(self, hg1, hg2, hg3):
        topics = ["profession", "hometown"]
        topic = random.choice(topics)
        self.bb.print_text(f"{hg1.name} shares stories about their {topic} with {hg2.name} and {hg3.name}.")
        self.swayed_event(hg1, hg2)
        self.swayed_event(hg1, hg3)
        self.swayed_event(hg2, hg1)
        self.swayed_event(hg3, hg1)
        
    def reminisce(self, hg1, hg2):
        topics = ["childhood", "family"]
        topic = random.choice(topics)
        self.bb.print_text(f"{hg1.name} and {hg2.name} reminisce about their {topic}.")
        self.swayed_event(hg1, hg2)
        self.swayed_event(hg2, hg1)
        
    def discuss_favorites(self, hg1, hg2):
        favorites = ["movies", "TV shows", "books", "music genres"]
        favorite = random.choice(favorites)
        self.bb.print_text(f"{hg1.name} and {hg2.name} discuss their favorite {favorite}.")
        self.swayed_event(hg1, hg2)
        self.swayed_event(hg2, hg1)
        
    def bond_over_hobby(self, hg1, hg2):
        hobbies = ["painting", "reading", "playing chess", "doing yoga", "working out"]
        hobby = random.choice(hobbies)
        self.bb.print_text(f"{hg1.name} and {hg2.name} bond over their shared love for {hobby}.")
        self.swayed_event(hg1, hg2, 2)
        self.swayed_event(hg2, hg1, 2)
        
    def help_with_chores(self, hg1, hg2):
        chores = ["washing dishes", "doing laundry", "cleaning the bathroom", "cooking dinner"]
        chore = random.choice(chores)
        self.bb.print_text(f"{hg1.name} helped {hg2.name} with {chore}.")
        self.swayed_event(hg1, hg2)
        self.swayed_event(hg2, hg1)
        
    ##### Calculations / Coding Stuff

    def swayed_event(self, hg, target, strength=None, debug=True):
        self.bb.make_formatting()
        if strength:
            to_add = strength
        else:
            to_add = random.randint(1, 2)
        self.added_info = (hg, hg.impressions.keys())
        new = hg.impressions[target.name] + to_add
        adj = min(10, new)
        hg.impressions[target.name] = max(1, adj)
        if self.bb.debug_impressions and debug:
            mid = f": +{to_add} with "
            imp_text = f"{hg.name}{mid}{target.name}"
            self.bb.formatting[mid] = self.bb.imp_color
            self.bb.print_text(imp_text)

    def unswayed_event(self, hg, target, strength=None, debug=True):
        self.bb.make_formatting()
        if strength:
            to_sub = strength
        else:
            to_sub = random.randint(1, 2)
        new = hg.impressions[target.name] - to_sub
        adj = min(10, new)
        hg.impressions[target.name] = max(1, adj)
        if self.bb.debug_impressions is True and debug == True:
            mid = f": -{to_sub} with "
            imp_text = f"{hg.name}{mid}{target.name}"
            self.bb.formatting[mid] = self.bb.imp_color
            self.bb.print_text(imp_text)

    def generate_alliance_name(self, members):
        if random.random() < 0.3:
            return random.choice(["The Leftovers", "The Outsiders", "The Misfits"])

        names = [
            re.sub(r"([A-Z])", r" \1", member.name[0]).split() for member in members
        ]
        return "".join([random.choice(name) for name in names]).upper()

    def imp_adjustment(self):
        for hg1 in self.houseguests:
            for hg2 in self.houseguests:
                if hg1 != hg2:
                    r = random.randint(-1, 1)
                    if r == 1:
                        self.swayed_event(hg1, hg2, 1, False)
                        self.swayed_event(hg2, hg1, 1, False)
                    elif r == -1:
                        self.unswayed_event(hg1, hg2, 1, False)
                        self.unswayed_event(hg2, hg1, 1, False)

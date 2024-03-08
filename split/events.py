import random
import re

from alliance import Alliance
from bberror import BBError
from constants import *


class Events():
    
    def __init__(self, big_brother):
        self.bb = big_brother
        
        self.houseguests = self.bb.houseguests

    # EVENTS ==================================================================
    def event_spawner(self, variety=None):
        self.houseguests = self.bb.houseguests
        if len(self.houseguests) > 3:
            try:
                self.bb.make_formatting()
                if variety is not None:
                    self.comp(self.houseguests, variety)
                else:
                    # Random events
                    for _ in range(random.randint(0, MAX_EVENTS)):
                        potential_hgs = [hg for hg in self.houseguests if hg not in self.bb.evicted_houseguests] 
                        print(potential_hgs) 
                        
                        # TODO: LINE CAUSING PROBLEMS
                        hg1, hg2, hg3 = random.sample(potential_hgs, 3)
                        
                        event_index = random.randint(0, 3)
                        if event_index == 0 and len(self.houseguests) >= 3:
                            self.event_1(hg1, hg2, hg3)
                        elif event_index == 1:
                            self.event_2(hg1, hg2)
                        elif event_index == 2 and len(self.houseguests) >= 4 and len(hg1.alliances) > 0:
                            self.event_3(hg1, hg2)
                        elif event_index == 3 and len(self.houseguests) >= 4:
                            self.event_5(hg1)
                        else:
                            self.event_4(hg1, hg2)
            except Exception as e:
                raise BBError(e, self.bb) from e

    def event_1(self, hg1, hg2, hg3):
        # Player pulls aside another player to tell them to target third player.
        # If succeeds, adds 2 to impressions for each hg other than the third who loses 2.

        self.bb.print_text(f"{hg1.name} pulls {hg2.name} aside to talk about {hg3.name}.")
        self.bb.print_text(f"{hg1.name}: You know, {hg2.name}, {hg3.name} is just no good...")
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

    def event_2(self, hg1, hg2):
        topic = self.get_fight_topic()
        self.bb.print_text(f"{hg1.name} gets in a fight with {hg2.name} over {topic}!")
        
        if hg1.friendliness > hg2.emotionality or hg2.friendliness > hg1.emotionality:
            self.bb.print_text(f"But their friendship is too strong! {hg1.name} and {hg2.name} made up!")
        elif hg1.friendliness == hg2.emotionality and hg2.friendliness == hg1.emotionality:
            self.bb.print_text(f"In a rare move, {hg1.name} and {hg2.name} agree to disagree!")
        else:
            hg1.target = hg2.name
            hg2.target = hg1.name
            self.unswayed_event(hg1, hg2, 3)
            self.unswayed_event(hg2, hg1, 3)
            self.bb.print_text(f"They're inconsolable! They both walk off in a huff after a screaming fit!")

    def get_fight_topic(self):
        topic = random.choice(fight_topics)
        if "{food}" in topic:
            foods = ["slice of pizza", "slice of cake", "cookie", "sandwich", "piece of fruit", "bag of chips"]
            topic = topic.replace("{food}", random.choice(foods))
        if "{drink}" in topic:
            drinks = ["bottle of wine", "beer", "soda", "juice", "cup of coffee", "glass of milk"]
            topic = topic.replace("{drink}", random.choice(drinks))
        if "{item}" in topic:
            items = ["towel", "book", "magazine", "remote control", "dirty dish", "piece of clothing"]
            topic = topic.replace("{item}", random.choice(items))
        if "{room}" in topic:
            rooms = ["kitchen", "living room", "bathroom", "bedroom"]
            topic = topic.replace("{room}", random.choice(rooms))
        if "{houseguest}" in topic:
            hgs = [hg.name for hg in self.houseguests]
            topic = topic.replace("{houseguest}", random.choice(hgs))
        return topic    
        

    def event_3(self, hg1, hg2):
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

    def event_4(self, hg1, hg2):
        # Casual conversation. 100% chance of increasing impression by 1 or 2.
        self.bb.print_text(f"{hg1.name} has a casual conversation with {hg2.name}.")
        self.swayed_event(hg1, hg2)

    def event_5(self, hg1):
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

    def swayed_event(self, hg, target, strength=None, debug=True):
        self.bb.make_formatting()
        if strength:
            to_add = strength
        else:
            to_add = random.randint(1, 2)
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
                        self.swayed_event(hg1, hg2,1,False)
                        self.swayed_event(hg2, hg1,1,False)
                    elif r == -1:
                        self.unswayed_event(hg1, hg2,1,False)
                        self.unswayed_event(hg2, hg1,1,False)
    
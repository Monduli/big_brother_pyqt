import random

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
        self.vetoed = False
        self.target = None
        self.impressions = {}
        self.alliances = []

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

    def join_alliance(self, alliance):
        self.alliances.append(alliance.name)

    def leave_alliance(self, alliance_name):
        if alliance_name in self.alliances:
            self.alliances.remove(alliance_name)

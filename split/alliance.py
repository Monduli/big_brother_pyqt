class Alliance:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.target = None

    def add_member(self, houseguest):
        self.members.append(houseguest)

    def set_target(self, target):
        self.target = target
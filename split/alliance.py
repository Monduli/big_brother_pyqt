class Alliance:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.target = None

    def add_member(self, houseguest):
        if houseguest not in self.members:
            self.members.append(houseguest)

    def set_target(self, target):
        self.target = target

    def remove_member(self, houseguest):
        if houseguest in self.members:
            self.members.remove(houseguest)

    def get_size(self):
        return len(self.members)

    def has_member(self, houseguest):
        return houseguest in self.members

    def clear_target(self):
        self.target = None

    def list_members(self):
        return self.members.copy()

    def is_target(self, houseguest):
        return self.target == houseguest

# Test the Alliance class
alliance = Alliance("The Strongest")
assert alliance.name == "The Strongest"
assert alliance.get_size() == 0

alliance.add_member("Alice")
alliance.add_member("Bob")
assert alliance.get_size() == 2
assert alliance.has_member("Alice")
assert alliance.has_member("Bob")

alliance.set_target("Eve")
assert alliance.target == "Eve"

alliance.remove_member("Bob")
assert alliance.get_size() == 1
assert not alliance.has_member("Bob")

# Adding a member that's already in the alliance should not increase its size
alliance.add_member("Alice")
assert alliance.get_size() == 1

# Clearing the target
alliance.clear_target()
assert alliance.target == None

# Listing members
members = alliance.list_members()
assert "Alice" in members
assert len(members) == 1

# Checking if someone is the target
assert not alliance.is_target("Alice")
alliance.set_target("Alice")
assert alliance.is_target("Alice")
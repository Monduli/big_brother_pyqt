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

FINALE_PHRASES = {
    (2,3): [
        "I'm leaning towards {name} since they were straight with me for the most part.",
        "{name} made several promises but held true on a few key ones that mattered to me.",
        "{name} wasn't perfect but they owned their game moves when we talked."
    ],
    (4,5): [
        "Despite a couple moments this summer, I really respect the way {name} conducted themselves in the game.",
        "My decision is to vote for {name} based on the overall rapport we built inside the house.",
        "{name} made a real effort to understand my perspective even when we disagreed."
    ],
    (6,7): [
        "Even with some bumps along the way, my vote is clearly for {name} in my eyes.",
        "No one played a perfect game, but I think {name} played the best overall if I'm being objective.",
        "{name} was one of my closest allies and I want to see good game play rewarded."
    ],
    (8,9): [
        "Hands down I have to vote for {name}. We were tight since early on and I gave them my word.",
        "Are you kidding? {name} has my vote 100%. We worked together as a tight partnership from Day 1.",
        "As much as I respect the other finalist, me and {name} were riding this to the end together no matter what."
    ],
    (10): [
        "I would never vote against you, {name}! After all we accomplished in this game, you so deserve the money!",
        "If I don't vote for my true ally {name}, I'd just be a bitter jerk. You know where my vote lands!",  
        "You did right by me, {name}. Now I'm doing right by you - you have my vote for the win and you know why!"
    ]
}

# retain_season: Saves to a file which season you are on. 
# This number increments every time you run a new season after a winner is declared, but at no other time.
from houseguest import HouseGuest

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
    (2, 3): [
        "I'm leaning towards {name} since they were straight with me for the most part.",
        "{name} made several promises but held true on a few key ones that mattered to me.",
        "{name} wasn't perfect but they owned their game moves when we talked.",
    ],
    (4, 5): [
        "Despite a couple moments this summer, I really respect the way {name} conducted themselves in the game.",
        "My decision is to vote for {name} based on the overall rapport we built inside the house.",
        "{name} made a real effort to understand my perspective even when we disagreed.",
    ],
    (6, 7): [
        "Even with some bumps along the way, my vote is clearly for {name} in my eyes.",
        "No one played a perfect game, but I think {name} played the best overall if I'm being objective.",
        "{name} was one of my closest allies and I want to see good game play rewarded.",
    ],
    (8, 9): [
        "Hands down I have to vote for {name}. We were tight since early on and I gave them my word.",
        "Are you kidding? {name} has my vote 100%. We worked together as a tight partnership from Day 1.",
        "As much as I respect the other finalist, me and {name} were riding this to the end together no matter what.",
    ],
    (10): [
        "I would never vote against you, {name}! After all we accomplished in this game, you so deserve the money!",
        "If I don't vote for my true ally {name}, I'd just be a bitter jerk. You know where my vote lands!",
        "You did right by me, {name}. Now I'm doing right by you - you have my vote for the win and you know why!",
    ],
}

# retain_season: Saves to a file which season you are on.
# This number increments every time you run a new season after a winner is declared, but at no other time.

fight_topics = [
    "the dishes",
    "who ate the last {food}",
    "who drank the last {drink}",
    "who flirts too much",
    "who snores",
    "who left {item} out",
    "who used all the hot water",
    "who left the {room} a mess",
    "who kept them up all night",
    "who is the biggest slob",
    "who is the biggest gossip",
    "who is the laziest",
    "who is the most annoying",
    "who is the biggest know-it-all",
    "who is the biggest attention seeker",
    "who is the biggest drama queen/king",
    "who is the biggest suck-up",
    "who is the biggest backstabber",
    "who is the biggest flirt",
    "who is the biggest complainer",
    "who is the biggest sore loser",
    "who is the biggest cheater",
    "who is the biggest liar",
    "who is the biggest loudmouth",
    "who is the biggest sellout",
    "who is the biggest hypocrite",
    "who is the biggest slacker",
    "who is the biggest party pooper",
    "who is the biggest control freak",
    "who is the biggest suck-up to {houseguest}",
    "who is the most two-faced",
    "who is the most untrustworthy",
    "who is the most selfish",
    "who is the most manipulative",
    "who is the most arrogant",
    "who is the most judgmental",
    "who is the most fake",
    "who is the most immature",
    "who is the most disrespectful",
    "who is the most ungrateful",
    "who is the biggest betrayer",
    "who is the biggest saboteur",
    "who is the biggest instigator",
    "who is the biggest troublemaker",
    "who is the biggest kiss-ass",
    "who is the biggest passive-aggressive",
    "who is the biggest gossip"
]

HOH_COMPS = [
    ("Flip the House", "ELIMINATION"),
    ("Majority Rules", "ELIMINATION"),
    ("Question the Quack", "ELIMINATION"),
    ("Counting Sheep", "FASTEST"),
    ("True or False", "ELIMINATION"),
    ("Memory Lane", "FASTEST"),
    ("Slip 'n Slide", "FASTEST"),
    ("Red Light, Green Light", "FASTEST"),
    ("Egg Heads", "ELIMINATION"),
    ("Spelling Bee", "ELIMINATION"),
    ("Domino Effect", "ELIMINATION"),
    ("Wheel of Fortune", "FASTEST"),
    ("Guess Who", "ELIMINATION"),
    ("Tug of War", "FASTEST"),
    ("Puzzle Frenzy", "FASTEST"),
]

VETO_COMPS = [
    ("Block the Veto", "ELIMINATION"),
    ("Knight Moves", "ELIMINATION"),
    ("Cry Me a Veto", "ELIMINATION"),
    ("Counting Votes", "FASTEST"),
    ("Fact or Fiction", "ELIMINATION"),
    ("Photographic Memory", "FASTEST"),
    ("Slip 'n Veto", "FASTEST"),
    ("Red Veto, Green Veto", "FASTEST"),
    ("Egg on Your Face", "ELIMINATION"),
    ("Spelling Veto", "ELIMINATION"),
    ("Veto Twist", "ELIMINATION"),
    ("Memory Recall", "FASTEST"),
    ("Veto Scramble", "FASTEST"),
    ("Veto Showdown", "ELIMINATION"),
    ("Veto Mastery", "FASTEST"),
]

legends_data = {
    "US2": ["Will", "Nicole", "Hardy", "Krista", "Justin", "Shannon", "Autumn", "Mike", "Sheryl", "Kent", "Bunky", "Monica"],
    "US3": ["Danielle", "Jason", "Lisa", "Marcellas", "Amy", "Roddy", "Chiara", "Gerry", "Josh", "Tonya", "Eric", "Lori"],
    "US4": ["Jun", "Alison", "Robert", "Erika", "Jack", "Nathan", "Dana", "Jee", "Justin", "Scott", "Amanda", "David", "Michelle"],
    "US5": ["Drew", "Michael", "Diane", "Nakomis", "Cowboy", "Adria", "Natalie", "Karen", "Will", "Jase", "Marvin", "Holly", "Mike", "Lori"],
    "US6": ["Maggie", "Ivette", "Janelle", "April", "Howie", "Kaysar", "Jennifer", "Rachel", "James", "Sarah", "Beau", "Eric", "Ashlea", "Michael"],
    "US7": ["Mike", "Erika", "Janelle", "Will", "Danielle", "George", "James", "Howie", "Marcellas", "Nakomis", "Diane", "Jase", "Alison", "Kaysar"],
    "US8": ["Dick", "Daniele", "Zach", "Jameka", "Eric", "Jessica", "Amber", "Dustin", "Jen", "Nick", "Kail", "Mike", "Carol", "Joe"],
    "US9": ["Adam", "Ryan", "Sheila", "Sharon", "James", "Chelsia", "Joshuah", "Natalie", "Matt", "Allison", "Alex", "Amanda", "Parker", "Neil", "Jacob"],
    "US10": ["Dan", "Memphis", "Jerry", "Keesha", "Renny", "April", "Ollie", "Michelle", "Libra", "Jessie", "Angie", "Steven", "Brian"],
    "US11": ["Jordan", "Natalie", "Kevin", "Michele", "Jeff", "Russell", "Lydia", "Jessie", "Chima", "Ronnie", "Casey", "Laura", "Braden"],
    "US12": ["Hayden", "Lane", "Enzo", "Britney", "Ragan", "Matt", "Brendon", "Kathy", "Rachel", "Andrew", "Kristen", "Monet", "Annie"],
    "US13": ["Rachel", "Porsche", "Adam", "Kalia", "Shelly", "Jordan", "Jeff", "Daniele", "Brendon", "Lawon", "Dominic", "Cassi", "Keith"],
    "US14": ["Ian", "Dan", "Danielle", "Shane", "Jenn", "Frank", "Joe", "Ashley", "Wil", "Janelle", "Mike", "Britney", "Willie", "JoJo"],
    "US15": ["Andy", "GinaMarie", "Spencer", "Judd", "McCrae", "Amanda", "Elissa", "Helen", "Aaryn", "Jessie", "Candice", "Howard", "Kaitlin", "Jeremy", "Nick", "David"],
    "US16": ["Derrick", "Cody", "Victoria", "Caleb", "Frankie", "Zach", "Donny", "Christine", "Nicole", "Hayden", "Jocasta", "Amber", "Brittany", "Devin", "Paola", "Joey"],
    "US17": ["Steve", "Liz", "Vanessa", "Austin", "Julia", "James", "Meg", "Jackie", "Becky", "Shelli", "Clay", "John", "Jason", "Audrey", "Jeff", "Da'Vonne", "Jace"],
    "US18": ["Nicole", "Paul", "James", "Natalie", "Corey", "Paulie", "Michelle", "Zakiyah", "Bridgette", "Da'Vonne", "Victor", "Bronte", "Tiffany", "Frank", "Glenn", "Jozea"],
    "US19": ["Josh", "Paul", "Christmas", "Kevin", "Alex", "Jason", "Raven", "Matt", "Mark", "Elena", "Cody", "Jessica", "Ramses", "Dominique", "Jillian", "Megan", "Cameron"],
    "US20": ["Kaycee", "Tyler", "JC", "Angela", "Sam", "Brett", "Haleigh", "Faysal", "Scottie", "Rockstar", "Bayleigh", "Rachel", "Kaitlyn", "Swaggy C", "Winston", "Steve"],
    "US21": ["Jackson", "Holly", "Nicole", "Cliff", "Tommy", "Christie", "Nick", "Analyse", "Jessica", "Kathryn", "Jack", "Sis", "Sam", "Bella", "Ovi", "Kemi", "David"],
    "US22": ["Cody", "Enzo", "Nicole F", "Christmas", "Memphis", "Tyler", "David", "Dani", "Kevin", "Day", "Ian", "Bayleigh", "Kaysar", "Janelle", "Nicole A", "Keesha"],
    "US23": ["Xavier", "Derek F", "Azah", "Kyland", "Hannah", "Tiffany", "Claire", "Alyssa", "Sarah Beth", "Derek X", "Britini", "Christian", "Whitney", "Brent", "Brandon", "Travis"],
    "US24": ["Taylor", "Monte", "Turner", "Brittany", "Alyssa", "Michael", "Terrance", "Kyle", "Joseph", "Jasmine", "Indy", "Ameerah", "Nicole", "Daniel", "Pooch", "Paloma"],
    "US25": ["TBA"],  # Update with actual houseguests when available
    "CA1": ["Jillian", "Gary", "Emmett", "Talla", "Andrew", "Topaz", "Alec", "Peter", "Liza", "Tom", "Suzette", "Danielle", "Aneal", "Kat", "AJ"],
    "CA2": ["Jon", "Neda", "Sabrina", "Heather", "Adel", "Allison", "Arlie", "Rachelle", "Ika", "Kenny", "Paul", "Sarah", "Kyle", "Andrew"],
    "CA3": ["Sarah", "Godfrey", "Ashleigh", "Pilar", "Zach", "Bruno", "Kevin", "Willow", "Brittnee", "Johnny", "Jordan", "Sindy", "Naeha", "Graig", "Risha"],
    "CA4": ["Nick & Phil", "Kelsey", "Tim", "Cassandra", "Joel", "Loveita", "Nikki", "Jared", "Maddy", "Ramsey", "Dallas", "Raul", "Mitch", "Christine", "Paige", "Sharry", "Veronica"],
    "CA5": ["Kevin", "Karen", "Demetres", "Ika", "Dillon", "Dre", "William", "Jackie", "Sindy", "Bruno", "Neda", "Emily", "Cassandra", "Gary", "Dallas", "Mark"],
    "CA6": ["Paras", "Kaela", "Derek", "Will", "Maddy", "Johnny", "Olivia", "Ali", "Erica", "Hamza", "Jesse", "Veronica", "Merron", "Rozina", "Andrew"],
    "CA7": ["Dane", "Anthony", "Kyra", "Mark", "Adam", "Sam", "Este", "Damien", "Kiki", "Cory", "Chelsea", "Eddie", "Kailyn", "Maki", "Laura"],
    "CA8": ["TBA"],  # Update with actual houseguests when available
    "CA9": ["TBA"],  # Update with actual houseguests when available
    "CA10": ["TBA"],  # Update with actual houseguests when available
}

def get_legends_houseguests(season):
    """
    Retrieves the list of houseguests for the specified season in Legends Mode.

    Args:
        season (int): The season number.

    Returns:
        list: A list of HouseGuest objects representing the houseguests for the specified season.

    Raises:
        KeyError: If the specified season is not found in the legends data.
    """
    if season not in legends_data:
        raise KeyError(f"Season {season} not found in legends data.")

    houseguests = []
    for name in legends_data[season]:
        houseguests.append(HouseGuest(name,season))

    return houseguests
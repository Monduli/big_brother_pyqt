# big_brother_pyqt
A Big Brother (US) simulator made in Python (uses PyQT for the interface). Early in development!

Big TODO: Fix the README. lol

Note that this was originally a terminal app and proper text is still being added to the PyQT interface.
If you feel something is missing from the interface, look at the terminal. If it's still missing, look at my TODO at the bottom of this README. If it's STILL missing, let me know.

On opening:
    The app will generate a list of 12 houseguests. If you want more, change NUM_PLAYERS at the top.
    They will all be given a random profession. Add more to PROFESSIONS if you want more variety or something else.

On "Continue":
    An HOH will be chosen randomly from the houseguests. Code is supposed to stop repeat HOHs from occurring, but it might be buggy.
    The HOH will nominate two players randomly. (not actually - see "under the hood")
    The HOH, nominees, and three randomly selected houseguests (outside of those three) will play in the POV.
    Someone will win the POV. They will then randomly decide to use the POV or not, or they will guaranteed use it to save themselves. (Marcellus behavior may be added later)
    At the end of the week, the houseguests will vote to evict someone. Who is evicted is random at the moment.

    If there are only 3 or less houseguests left, they will not play for the POV (if you don't know, with 3 houseguests, the HOH nominates the two remaining. with 2 left, there are no comps).
    At the final 2, the two remaining houseguests will "plead their case", which is meaningless at the moment.
    Afterwards, in the terminal, you will see which evicted houseguests voted for who. A winner will be declared.

On "Reset":
    Resets the game. Currently breaks some of the buttons, though.

Under the hood: 
    Each houseguest has five underlying statistics that control how their game generally goes.
    They also have a dictionary (hashmap, a collection of words attached to values) that has their impression about other houseguests.
    Their impressions of the houseguests are set randomly at the beginning, but change depending on the random events that happen.
    For instance, if Joe pulls Amy over to talk privately about Bill, their impressions of Bill will decrease.
    Amy's will decrease by 2, while Joe's will decrease by 1 (as cementing negativity about another person can cause you to like them less too).
    Their impression determines who will be put on the block if they are HOH. It will either be the two houseguests with the lowest impression values, or their target.
    Their target is also set by random event. Currently, the event is their Alliance deciding someone should go on the block.

Noted bugs as of 2/3/2024:
    - Reset doesn't work right. 
    - Any actions taken after someone wins is buggy.
    - Sometimes, someone will get vetoed and evicted anyway. Cheap trick, but an illegal move.
    - Sometimes, the "renoms" will be the same as the noms, indicating the veto was used, but not on one of the nominees.
    - Not sure if this was fixed already, but sometimes the app will declare an evicted houseguest as the winner, but in the terminal will indicate the actual winner. Additionally, sometimes the added up votes don't actually reflect the winner.

TODO:
    - Slow down the process so there's some tension. Currently, it's like gurgitating a whole week of Big Brother. (Kind of like BBCAN7 where you knew exactly what was going to happen, so it kinda sucks as much as I really like Dane)
    - Alliances (will try to avoid super alliances or whatever tf they're called that make the game extremely boring)
    - Drama, aka: Make all the made moves make sense
        - Actions taken between comps to shift the game around (so Maggie can convince Howie to evict his teammates)
        - Don't nominate people in your alliance (unless you're Howie lol)
    - Give everyone stats that will be invisible to the viewer (by default) but will influence the likelihood of making particular moves ()
    - Assign arrays of relationship scores, so everyone has a disposition towards every other individual. This will also affect move-making and alliances.
    - Improve the UI. I know the reset and continue buttons look funky. This was hastily thrown together while I was working, and I will fix it.
    - Bug fixes, obviously. And I don't mean that grasshopper or cricket or whatever from that one season. If it gets introduced, the mime from BB4 isn't a bug. Just fyi.
    - Turn the .py into a .exe so it's easier for non-programmers to use. (.py files are really easy to run if you have Python, but most regular people are used to .exe's)

Additions (Feb 8):
    Dark mode.
    Statistics for gameplay. (see "under the hood")
    Random events.
    Impressions button.
    Houseguests will now target each other and nominate accordingly.

Bug fixes (Feb 8):
    Fixed a situation where the same person was being nominated twice in the same week. At the same time. Brutal, I know.
    Fixed numerous crashes, mostly to do with implementing the new features.
    Fixed a bug where the veto holder was immediately re-nominated after vetoing themselves.

New bugs (Feb 8):
    Clicking reset and then impressions will crash the program.
    

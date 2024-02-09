# big_brother_pyqt

A Big Brother (US) simulator made in Python (uses PyQT for the interface). Early in development!

## Overview

This was originally a terminal app and proper text is still being added to the PyQT interface. If you feel something is missing from the interface, look at the terminal. If it's still missing, see the TODO section below.

### On opening:

- The app will generate a list of 12 houseguests. To change the number, update `NUM_PLAYERS` at the top of the code.
- Houseguests are assigned a random profession. Add more to `PROFESSIONS` for more variety.

### On "Continue":

- An HOH is randomly chosen. Code prevents repeat HOHs.
- The HOH nominates two players based on impressions and targets (see "Under the Hood" below). 
- The HOH, nominees, and 3 randomly selected houseguests play in the POV competition.
- Someone wins the POV and decides randomly whether to use it or not, unless they won it themselves.
- Houseguests vote to evict someone. For now this is random.
- With 3 or fewer players left, there is no POV competition.
- At the final 2, the remaining houseguests give speeches, which currently do nothing.
- In the terminal, you'll see who the evicted houseguests voted for and a winner is declared.

### On "Reset":

- Resets the game. Currently breaks some buttons.

## Under the Hood

- Each houseguest has 5 underlying statistics that influence their gameplay.
- They have an impressions dictionary with values for each other houseguest.
- Impressions are set randomly at the start but change based on random events. 
- Impressions determine nominations: either the bottom 2, or their target.
- Targets are set randomly via events like an Alliance deciding on someone.

## TODO

- Slow down the process for more tension.
- Implement Alliances.
- Create an executable for non-programmers.  
- Make statistics influence voting off.
- Add randomly generated competition flavor text.

## Additions (Feb 8)

- Dark mode
- Gameplay statistics 
- Random events
- Impressions button
- Houseguests now target and nominate others

## Bug Fixes (Feb 8) 

- Fixed duplicate nominations
- Fixed various crashes from new features  
- Fixed re-nomination after veto bug
- Fixed reset button position

## Remaining Bugs
Last updated 02/09/2024

### Crashes

- Clicking reset and then impressions crashes the program.
- Calling `play_week()` after game ends with 2 players left causes crash.

### Gameplay

- HOH is chosen from already evicted players if all remaining players have been HOH.
- Players can be nominated twice in the same week.
- Veto holder can win veto and not use it on themselves if they are a nominee.
- Evicted houseguests can still be nominated after being evicted.

### UI/UX

- Renominations don't show properly in UI text.
- Text box doesn't scroll automatically with new text added.
- Impressions matrix doesn't update with latest values when opened.

### Other

- Alliances feature not fully implemented.
- Voting off players is still random, not based on impressions.
- No real gameplay comp events yet.
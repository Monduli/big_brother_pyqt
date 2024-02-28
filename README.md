# big_brother_pyqt

A Big Brother (US) simulator made in Python (uses PyQT for the interface). Early in development!

## Overview

### On opening:

- The app will generate a list of 12 houseguests.
- Houseguests are assigned a random profession.

### Important distinction: Proceed is one action at a time. Conclude Week is the whole week at once.

- An HOH is randomly chosen. Code prevents repeat HOHs.
- The HOH nominates two players based on impressions and targets (see "Under the Hood" below). 
- The HOH, nominees, and 3 randomly selected houseguests play in the POV competition.
- Someone wins the POV and decides randomly whether to use it (guaranteed if they are nominated) or not
- Houseguests vote to evict someone. Alliances do factor into it somewhat.
- With 3 or fewer players left, there is no POV competition.
- At the final 2, the winner is chosen.

### On "Reset":

- Resets the game.

## Under the Hood

- Each houseguest has 5 underlying statistics that influence their gameplay.
- They have an impressions dictionary with values for each other houseguest.
- Impressions are set randomly at the start but change based on random events. 
- Impressions determine nominations: either the bottom 2, or their target.
- Targets are set randomly via events like an Alliance deciding on someone.
- Alliances form randomly. Currently the names they pick are dumb, but that's not so far off from half the alliances on the show anyway.

## TODO

- Improve alliances.
- Create an executable for non-programmers.  
- Make more statistics influence actions.
- Improve comps.

## Remaining Bugs
Last updated 02/28/2024

### Crashes

- There are some issues with Conclude Week if you're in the middle of a week via Proceed.

### Gameplay

- All fixed for now!

### UI/UX

- All fixed for now!

### Other

- All fixed for now!
# Mazefinder
## Description:
### In a gist:

This was initially for CS50P's final project, but I'm failing to find working functions that are easily testable with pytest without changing a whole lot or making things feel weirder than they are already. Will be making another... simpler, non "graphical" project, probably just for CS50P.

A simple CLI game using the curses library.

Generates a random maze every run. Size of the maze varies per terminal size up to a maximum of 199 x 199 (maze sizes must be kept odd for proper generation.)

Player can then travel through the maze and reach the exit, then winning.

That's it. Never said it was... fun. But there it is.
Admittedly, this wasn't the best project idea to content the project's requirements.

### In more details:

### Implemented a class named Maze that handles:
1. Generating the maze

We start with generating a three dimensional dictionnary, using tuples as the coordinate system and their values as the "cell sprite," empty, wall, exit, player, ... it starts as all painted as walls.

We then have a function that algorithmatically carve paths through the entire dictionary, ensuring no gap between paths of more than 1 wall is left anything in the maze.

3. Drawing the maze in the terminal using the curses library.

### Implemented a short class named Player that handles:
1. Player graphic - simply changes the instantiated Maze object's map coordinate to the right graphic as the player moves places.

2. Player coordinate - simply stores and change the player's coordinates as needed.

3. Player movement - Really handles the two above options via user input (WASD, Arrow Keys)

### There is also three top-level functions:
Last two really added just to satisfy the Final Project's requirements, so they admittedly could be in a class or something else:
1. Splash Screen - Main menu with fancy ASCII art slowly drawn on start-up.

2. Check if Player is at Maze Exit.

3. Screen redraws when player confirmed to have found the exit; Win card.

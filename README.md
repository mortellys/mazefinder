# Mazefinder
#### Video Demo: https://www.youtube.com/watch?v=Y63W7yuoEPc
#### Description:
### In a gist:
A simple CLI game using the curses library.

Generates a random maze every run. Size of the maze varies per terminal size, maxed-up reasonably, or chosen by the player in options.

Player can then travel through the maze and reach the exit, then winning.

That's it. Never said it was... fun. But there it is.

Honestly, felt like I tried to chew on more than I should have. A lot of this code I feel could be... much better, yet it all works pretty well... at least as far as I could test it.
Anyhow, not a very useful thing all things considered! But it got me learning at least, so I'm satisfied at this point.

### In more details:

### Implemented a class named Maze that handles:
1. Generating the maze

We start with generating a three dimensional dictionnary, using tuples as the coordinate system and their values as the "cell sprite," empty, wall, exit, player, ... it starts as all painted as walls.

2. We then have a function that algorithmatically carve paths through the entire dictionary, ensuring no gap between paths of more than 1 wall is left anything in the maze.

3. Drawing the maze in the terminal using the curses library - by default the above carving as the maze is generated can be seen visually.

### Implemented a short class named Player that handles:
1. Player graphic - simply changes the instantiated Maze object's map coordinate to the right graphic as the player moves places.

2. Player coordinate - simply stores and change the player's coordinates as needed.

3. Player movement - Really handles the two above options via user input (WASD, Arrow Keys)

### There is also some top-level functions:
Last two really added just to satisfy the Final Project's requirements, so they admittedly could be in a class or something else:
1. Splash Screen - Main menu with fancy ASCII art slowly drawn on start-up.

2. Check if Player is at Maze Exit.

3. Screen redraws when player confirmed to have found the exit; Win card.

4. Validity checks for options

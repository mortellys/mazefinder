"""
"Mazefinder - Simple CLI game"
by mortellys (alex e.)
Goal: Lead your character through a random maze. Simple as. Am sure this has been done before.

This was initially for CS50P's final project, but I'm failing to find working functions that are easily testable with pytest without changing a whole lot.
Will be making another... simpler, non "graphical" project, probably just for CS50P.

Thus:
    [x] 0. Splash screen menu (Press A to Start + Art kinda thing, why not?) <-- Not sure why this was my numero uno priority lol
    [x] 1. Generate the maze randomly
        [x] 1.1 Generate and display the actual maze.
        [x] 1.2 Place exit.
        [x] 1.3 Place player at start of maze gen.
    [x] 2. Player movement and victory condition
    [x] 3. Winning Card + Exit
    -- Extras --
    [ ] 3. Add options
        [ ] 3.1. Maze Size (defaults / max terminal size, manual input (max->termsize~)) as a choice
        [ ] 3.2. Maze Display (Show Generation / Instant Play) as a choice
        [ ] 3.3. Maze Display Gen Speed (min: 1ms, max: 100ms) as an int
        [ ] 3.4. Maze Gen Seed (default: random, manual input) as an int
    [ ] 4. Colors? Perhaps.
    [ ] 5. Profit?

For now, this really isn't meant to be a difficult game, the whole maze is visible
and the path to the exit is also clearly seeable.

⚠️ My interest in this isn't all that high, likely won't "finish it,"
it was mostly to prove myself able to get things done without crutching on following tutorials, etc.
For that, I am proud to have done it mostly. 👏

I warrant there are a lot of things in this code that could be redone more efficiently, no doubt.
Some of the odd choices were me trying to adhere to the CS50P final project requirements (top-level functions w/ unit tests mostly), but ah well.
"""

# If on windows, you will have to install windows-curses with:
# << pip install windows-curses >>
import curses, random, sys

# Most of the actual gen is referenced from
# https://inventwithpython.com/recursion/chapter11.html
# Re-adapted as a class and modified to fit my needs.
class Maze():
    def __init__(self, width=199, height=199, drawGen=True, drawSpeed=10, seed=None):
        if seed == None:
            random.seed(random.randint(0, 1024))
        else:
            random.seed(seed)
        if width >= curses.COLS - 2:
            self.WIDTH = curses.COLS - 4 if (curses.COLS - 4) % 2 else curses.COLS - 5
        else:
            self.WIDTH = width if width % 2 else width + 1
        if height >= curses.LINES - 8:
            self.HEIGHT =  curses.LINES - 10 if (curses.LINES - 10) % 2 else curses.LINES - 11
        else:
            self.HEIGHT = height if height % 2 else height + 1

        self.drawGen = drawGen
        self.drawSpeed = drawSpeed

        self.EMPTY = " "
        self.WALL = chr(9608) # Character 9608 is '█'
        self.NORTH, self.SOUTH, self.EAST, self.WEST = 'n', 's', 'e', 'w'
        self.EXIT = chr(9621) # Character 9621 is '▕'
        self.ExitPos = ()

        self.map = {}


    def generate(self, screen, x=1, y=1):
        for w in range(self.WIDTH): # x /cols
            for h in range(self.HEIGHT): # y /rows/lines
                self.map[(w, h)] = self.WALL # We begin with a walls-only map.
        self.seenCells = [(x, y)]
        self.carve(screen, x, y)
        # Randomly carve out paths through out the map.
        if not self.drawGen:
            self.draw(screen)

    def carve(self, screen, x, y):
        self.map[(x, y)] = self.EMPTY
        if self.drawGen:
            self.draw(screen)
        while True:
            unseenCells = []
            # These basically creates a small pocket around
            # the current position to see where the random gen
            #  can head next later in the loop (RECURSIVE section)
            if y > 1 and (x, y - 2) not in self.seenCells:
                unseenCells.append(self.NORTH)
            if y < self.HEIGHT - 2 and (x, y + 2) not in self.seenCells:
                unseenCells.append(self.SOUTH)
            if x > 1 and (x - 2, y) not in self.seenCells:
                unseenCells.append(self.WEST)
            if x < self.WIDTH - 2 and (x + 2, y) not in self.seenCells:
                unseenCells.append(self.EAST)

            if len(unseenCells) == 0:
                # DEAD END REACHED. Time to backtrack:
                return
            else:
                # RECURSIVE Section
                # Pick a random unseen cell to move to:
                nextIntersection = random.choice(unseenCells)

                if nextIntersection == self.NORTH:
                    nextX = x
                    nextY = y - 2
                    self.map[(x, y - 1)] = self.EMPTY
                elif nextIntersection == self.SOUTH:
                    nextX = x
                    nextY = y + 2
                    self.map[(x, y + 1)] = self.EMPTY
                elif nextIntersection == self.WEST:
                    nextX = x - 2
                    nextY = y
                    self.map[(x - 1, y)] = self.EMPTY
                elif nextIntersection == self.EAST:
                    nextX = x + 2
                    nextY = y
                    self.map[(x + 1, y)] = self.EMPTY

                # Sets the exit in a very lazy way.
                # The first time we get to the right-est edge, plop the exit there, that's it. Simple as.
                if (x == self.WIDTH - 2 and not self.ExitPos):
                    self.ExitPos = (x + 1, y)
                    self.map[self.ExitPos] = self.EXIT

                self.seenCells.append((nextX, nextY))
                self.carve(screen, nextX, nextY)

    def draw(self, screen):
        """Draws the maze. If called during every carve, it'll display the maze
        being created at whatever {drawSpeed} milliseconds.
        """

        # Some will balk at this code for not re-using the already existing dictionary... I mean, I do too.
        # Recreate the map as a straight list of strings, easier to work with than the dictionary, for drawing.
        # ... Mostly just because I want it to be all centered in the terminal.
        # and I am not smart enough yet to understand efficiency super well.
        Y_OFFSET = 9 # Avoid drawing over the top borders and the title card
        X_OFFSET = 1 # Avoid drawing over the left borders
        leading_whitespaces = " " * int(((curses.COLS - 2) - self.WIDTH) / 2) # This is the 2nd secret little sauce that centers it all.
        centered_map = []
        for y in range(self.HEIGHT): # rows/lines
            string = leading_whitespaces
            for x in range(self.WIDTH): # cols
                string += self.map[(x, y)]
            centered_map.append(string)

        for y in range(len(centered_map)):
            for x in range(len(centered_map[y])):
                # We lazily skip over drawing any blank characters for now.
                screen.addch(y+Y_OFFSET, x+X_OFFSET, centered_map[y][x])

        screen.refresh()
        curses.napms(self.drawSpeed)

class Player():
    def __init__(self):
        self.Icon = chr(9673)
        self.Position = {"x": 1, "y": 1}

    def move(self, direction, maze, screen):
        maze.map[(self.Position["x"], self.Position["y"])] = maze.EMPTY
        match direction:
            case "N":
                if self.checkForEmptyOrExit(self.Position["x"], self.Position["y"] - 1, maze):

                    self.Position["y"] -= 1
            case "S":
                if self.checkForEmptyOrExit(self.Position["x"], self.Position["y"] + 1, maze):
                    self.Position["y"] += 1
            case "W":
                if self.checkForEmptyOrExit(self.Position["x"] - 1, self.Position["y"], maze):
                    self.Position["x"] -= 1
            case "E":
                if self.checkForEmptyOrExit(self.Position["x"] + 1, self.Position["y"], maze):
                    self.Position["x"] += 1
        maze.map[(self.Position["x"], self.Position["y"])] = self.Icon
        maze.draw(screen)

    def checkForEmptyOrExit(self, x, y, maze):
        return (maze.map[(x, y)] == maze.EMPTY or maze.map[(x, y)] == maze.EXIT)

def main(screen):
    if (curses.COLS < 80 or curses.LINES < 15):
        sys.exit("Terminal screen is too small;\nMinimum: 81w x 15h")

    # These are temporary for now... plan to add as user-settable options later, maybe.
    w, h = 81, 41 # Numbers MUST be odds
    seed = None
    draw = True
    speed = 10

    # screen.box()
    curses.curs_set(0)
    splash_screen(screen)
    # Splash Menu
    while True:
        key = screen.getkey()
        if key == "q" or key == "Q":
            sys.exit()
        elif key == "a" or key == "A":
            maze = Maze(w, h, draw, speed, seed)
            maze.generate(screen)
            player = Player()
            maze.map[(player.Position["x"], player.Position["y"])] = player.Icon
            maze.draw(screen)
            break
        curses.napms(5)

    # Gaming
    while True:
        key = screen.getch()
        if (key == 259 or key == 119 or key == 87):
            player.move("N", maze, screen)
            # up: 259     w: 119 W: 87
        elif (key == 258 or key == 115 or key == 83):
            player.move("S", maze, screen)
            # down: 258   s: 115 S: 83
        elif (key == 260 or key == 97 or key == 65):
            player.move("W", maze, screen)
            # left: 260   a: 97  A: 65
        elif (key == 261 or key == 100 or key == 68):
            player.move("E", maze, screen)
            # right: 261  d: 100 D: 6
        curses.napms(5)
        if playerAtExit(player.Position["x"], player.Position["y"], maze.ExitPos):
            youAreWinner(screen)
            key = screen.getkey()
            if key == "q" or key == "Q":
                sys.exit()
            # end screen to do


def splash_screen(screen):
        SPLASH = []
        try:
            with open("splashart.txt", "r") as SPLASH_FILE: # Art generated with https://www.asciiart.eu/text-to-ascii-art
                for x in SPLASH_FILE:
                    SPLASH.append(x.replace("\n", ""))
            longest = len(max(SPLASH, key=len))
        except OSError:
            sys.exit("splashart.txt is missing")

        SPLASH_TEXT = ["", "A small, silly CLI game about mazes.", "", "Press A to Start", "Q to quit"]
        # This lets me perfectly center any text I need with the splash art.

        for txt in SPLASH_TEXT:
            SPLASH.append(txt.center(longest, " "))

        # and this nifty little guy centers everything to the terminal! (or well-enough)
        for i, line in enumerate(SPLASH):
            SPLASH[i] = line.center(curses.COLS - 2, " ")


        for y in range(len(SPLASH)):
            for x in range(len(SPLASH[y])):
                # We lazily skip over drawing any blank characters for now.
                if SPLASH[y][x] == " ":
                    continue
                screen.addch(y+1, x+1, SPLASH[y][x])
                screen.refresh()
                curses.napms(5)

        return 1

def playerAtExit(x, y, exitPos):
    return (x, y) == exitPos

def youAreWinner(screen):
    screen.clear()
    WIN = []
    WIN_TXT = ["", "Congrats, you are winner!", "Press Q to quit"]
    for txt in WIN_TXT:
        WIN.append(txt.center(curses.COLS - 2, " "))
    for y in range(len(WIN)):
        for x in range(len(WIN[y])):
            # We lazily skip over drawing any blank characters for now.
            if WIN[y][x] == " ":
                continue
            screen.addch(y+1, x+1, WIN[y][x])
            screen.refresh()

if __name__ == "__main__":
    # Wrapper handles exceptions much more cleanly than doing things yourself with try...except...
    # It also initializes: cbreak, noecho, keypad TRUE, and colors, restores it all itself on exit as well.
    curses.wrapper(main)

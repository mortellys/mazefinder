"""
"Mazefinder - Simple? CLI game"
by mortellys (alex e.)
Goal: Escape through a random maze. Simple as. Definitely done before.

Checklist:
    [x] 0. Splash screen menu (Press A to Start + Art kinda thing, why not?) <-- Not sure why this was my numero uno priority lol
    [x] 1. Generate the maze randomly
        [x] 1.1 Generate and display the actual maze.
        [x] 1.2 Place exit.
        [x] 1.3 Place player at start of maze gen.
    [x] 2. Player movement and victory condition
    [x] 3. Winning Card + Exit
    -- Extras --
    [x] 3. Add options
        [x] 3.1. Maze Size (defaults / max terminal size, manual input (max->termsize~)) as a choice
        [x] 3.2. Maze Display (Show Generation / Instant Play) as a choice
        [x] 3.3. Maze Display Gen Speed (min: 1ms, max: 100ms) as an int
        [x] 3.4. Maze Gen Seed (default: random, manual input) as an int
        -- [ ] 3.5. Save options locally for next boot? -- Scratched off, I wanna move to a new project.
    --[ ] 4. Colors? Perhaps.-- Tried a little, but seems too inconsistent from term to term...
    colors.RED & /.YELLOW in my vscode term just gives me pure black. 😂

For now, this really isn't meant to be a difficult game, the whole maze is visible
and the path to the exit is also clearly seeable.

I warrant there are a lot of things in this code that could be redone more efficiently, no doubt.
Some of the odd choices were me trying to adhere to the CS50P final project requirements (top-level functions w/ unit tests mostly), but ah well.
"""

# If on windows, you will have to install windows-curses with:
# << pip install windows-curses >>
import curses
import random
import sys
import copy
from curses.textpad import Textbox, rectangle
SPLASH_Y_OFFSET = 9     # Avoid drawing over the top borders and the title card
BORDER_X_OFFSET = 1     # Avoid drawing over the borders

class Maze():
    def __init__(self, options):
        if options["Maze Seed"] == 0:
            random.seed(random.randint(1, 1024) * random.randint(1, 1024))
        else:
            random.seed(options["Maze Seed"])
        if options["Maze Width"] >= curses.COLS - 2:
            self.WIDTH = curses.COLS - 4 if (curses.COLS - 4) % 2 else curses.COLS - 3
        else:
            self.WIDTH = options["Maze Width"] if options["Maze Width"] % 2 else options["Maze Width"] - 1
        if options["Maze Height"] >= curses.LINES - 8:
            self.HEIGHT = curses.LINES - 10 if (curses.LINES - 10) % 2 else curses.LINES - 9
        else:
            self.HEIGHT = options["Maze Height"] if options["Maze Height"] % 2 else options["Maze Height"] - 1

        self.drawGen = options["Draw Generation"]
        self.drawSpeed = options["Generation Speed"]

        self.EMPTY = " "
        self.WALL = chr(9608)  # Character 9608 is '█'
        self.NORTH, self.SOUTH, self.EAST, self.WEST = 'n', 's', 'e', 'w'
        self.EXIT = chr(9621)  # Character 9621 is '▕'
        self.ExitPos = ()

        self.map = {}

    # Most of the actual gen is referenced from
    # https://inventwithpython.com/recursion/chapter11.html
    # Re-adapted as a class and modified to fit my needs.
    def generate(self, screen, x=1, y=1):
        for w in range(self.WIDTH):  # x /cols
            for h in range(self.HEIGHT):  # y /rows/lines
                self.map[(w, h)] = self.WALL  # We begin with a walls-only map.
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
        # This is the 2nd secret little sauce that centers it all.
        leading_whitespaces = " " * (((curses.COLS - 2) - self.WIDTH) // 2)
        centered_map = []
        for y in range(self.HEIGHT):  # rows/lines
            string = leading_whitespaces
            for x in range(self.WIDTH):  # cols
                string += self.map[(x, y)]
            centered_map.append(string)

        for y in range(len(centered_map)):
            for x in range(len(centered_map[y])):
                # We lazily skip over drawing any blank characters for now.
                screen.addch(y+SPLASH_Y_OFFSET, x+BORDER_X_OFFSET, centered_map[y][x])

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
    maxh, maxw = screen.getmaxyx()
    if (maxw < 80 or maxh < 21):
        sys.exit("Terminal screen is too small;\nMinimum: 81w x 21h")
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    maxh = maxh - 1 if (maxh - SPLASH_Y_OFFSET) % 2 else maxh
    maxw = maxw - 1 if (maxw - BORDER_X_OFFSET) % 2 else maxw

    options = {"Maze Width": maxw, "Maze Height": maxh,
               "Maze Seed": 0, "Generation Speed": 10, "Draw Generation": True}

    # screen.box()
    curses.curs_set(0)
    splash_screen(screen)
    # Splash Menu
    while True:
        key = screen.getch()
        if key == ord("q") or key == ord("Q"):
            sys.exit()
        elif key == ord("o") or key == ord("O"):
            options = options_menu(screen, options)
            screen.clear()
            splash_screen(screen)
        elif key == ord("s") or key == ord("S"):
            screen.move(SPLASH_Y_OFFSET, 1)
            screen.clrtobot()
            maze = Maze(options)
            maze.generate(screen)
            player = Player()
            maze.map[(player.Position["x"], player.Position["y"])] = player.Icon
            maze.draw(screen)
            # Gaming
            while True:
                key = screen.getch()
                if (key == curses.KEY_UP or key == ord("w") or key == ord("W")):
                    player.move("N", maze, screen)
                elif (key == curses.KEY_DOWN or key == ord("s") or key == ord("S")):
                    player.move("S", maze, screen)
                elif (key == curses.KEY_LEFT or key == ord("a") or key == ord("A")):
                    player.move("W", maze, screen)
                elif (key == curses.KEY_RIGHT or key == ord("D") or key == ord("D")):
                    player.move("E", maze, screen)
                elif (key == ord('q') or key == ord('Q')):
                    sys.exit()
                curses.napms(5)
                if player_at_exit(player.Position["x"], player.Position["y"], maze.ExitPos):
                    is_winner(screen)
                    break
        curses.napms(1)


def splash_screen(screen):
    SPLASH = []
    try:
        with open("splashart.txt", "r") as SPLASH_FILE:  # Art generated with https://www.asciiart.eu/text-to-ascii-art
            for x in SPLASH_FILE:
                SPLASH.append(x.replace("\n", ""))
        longest = len(max(SPLASH, key=len))
    except OSError:
        sys.exit("splashart.txt is missing")

    SPLASH_TEXT = ["", "A small, silly CLI game about mazes.", "", "[S]tart  [O]ptions  [Q]uit"]
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
            curses.napms(2)


def options_menu(screen, menu):
    menu_bak_copy = copy.deepcopy(menu)
    maxh, maxw = screen.getmaxyx()
    maxh = maxh - 1 if (maxh - SPLASH_Y_OFFSET) % 2 else maxh
    maxw = maxw - 1 if (maxw - BORDER_X_OFFSET) % 2 else maxw

    # Values used outside the option selection
    current_row = 0
    current_opt = "Maze Width"
    opt_selected = False
    opt_y = 0
    # opt_x = 0 # unused
    opt_x_val = 0

    # Option selection
    while True:
        if menu["Maze Seed"] == 0:
            menu["Maze Seed"] = "Random"
        idx = 0
        screen.move(SPLASH_Y_OFFSET, BORDER_X_OFFSET)
        screen.clrtobot()
        for option, value in menu.items():
            x_opt = maxw//2 - len(option)
            x_val = maxw//2 + 3
            # y = maxh//2 - len(menu)//2 + idx + 2 # This will vertically center the options, which is great, but looks silly on bigger screens.
            y = SPLASH_Y_OFFSET + idx + 2

            # Colors the current selection
            if idx == current_row:
                current_opt = option
                screen.attron(curses.color_pair(1))
                screen.addstr(y, x_opt, f"{current_opt}")
                screen.attroff(curses.color_pair(1))
                screen.addstr(y, x_val, f"{value}")
                # Extract position value of current option
                if opt_selected:
                    opt_y = y
                    # opt_x = x_opt # unused
                    opt_x_val = x_val

            else:
                screen.addstr(y, x_opt, f"{option}")
                screen.addstr(y, x_val, f"{value}")
            idx += 1
        # y_helper = maxh//2 - len(menu)//2 + idx + 3
        y_helper = SPLASH_Y_OFFSET + idx + 3
        txt_helper = "[S]ave and go back    [R]eturn without saving"
        screen.addstr(y_helper, maxw//2 - len(txt_helper)//2, txt_helper)
        screen.refresh()

        # Option handlers
        if opt_selected:
            match current_opt:
                case "Maze Width":
                    while True:
                        new_val = grab_value(screen,
                                             opt_y,
                                             opt_x_val,
                                             "Maze Width",
                                             5,
                                             f"Min: 5, Max: {maxw} - ODD ONLY    How wide the maze will be    [ENTER] when finished")
                        try:
                            new_val = valid_sizes(new_val, maxw)
                            menu["Maze Width"] = new_val
                            screen.move(SPLASH_Y_OFFSET-1, 1)
                            screen.clrtobot()
                            break
                        except ValueError:
                            screen.refresh()
                            continue

                case "Maze Height":
                    while True:
                        new_val = grab_value(screen,
                                             opt_y,
                                             opt_x_val,
                                             "Maze Height",
                                             5,
                                             f"Min: 5, Max: {maxh} - ODD ONLY    How tall the maze will be    [ENTER] when finished")
                        try:
                            new_val = valid_sizes(new_val, maxh)
                            menu["Maze Height"] = new_val
                            screen.move(SPLASH_Y_OFFSET-1, 1)
                            screen.clrtobot()
                            break
                        except ValueError:
                            screen.refresh()
                            continue
                case "Maze Seed":
                    while True:
                        new_val = grab_value(screen,
                                             opt_y,
                                             opt_x_val,
                                             "Maze Seed",
                                             6,
                                             f"0 = Random, Range: [1, 99999]   Smaller map = less randomness    [ENTER] when finished")
                        try:
                            new_val = valid_seed(new_val)
                            menu["Maze Seed"] = new_val
                            screen.move(SPLASH_Y_OFFSET-1, 1)
                            screen.clrtobot()
                            break
                        except ValueError:
                            screen.refresh()
                            continue
                case "Generation Speed":
                    while True:
                        new_val = grab_value(screen,
                                             opt_y,
                                             opt_x_val,
                                             "Generation Speed",
                                             6,
                                             f"Min: 1ms, Max: 1000ms    How fast the maze gen is drawn    [ENTER] when finished")
                        try:
                            new_val = valid_gen_speed(new_val)
                            menu["Generation Speed"] = new_val
                            screen.move(SPLASH_Y_OFFSET-1, 1)
                            screen.clrtobot()
                            break
                        except ValueError:
                            screen.refresh()
                            continue
                case "Draw Generation":
                    if menu["Draw Generation"] == False:
                        menu["Draw Generation"] = True
                    else:
                        menu["Draw Generation"] = False
                case _:
                    sys.exit("Options menu resolved abnormally: unknown value")
            opt_selected = False
            continue

        # Selection keystroke handler
        key = screen.getch()
        if (key == curses.KEY_UP) and current_row > 0:
            current_row -= 1
        elif (key == curses.KEY_DOWN) and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_opt in menu:
                opt_selected = True
        elif key == ord("s") or key == ord("S"):
            return menu
        elif key == ord("r") or key == ord("R"):
            return menu_bak_copy


def grab_value(screen, y, x, option, maxChar, tooltip):
    _, maxw = screen.getmaxyx()
    # maxh = maxh - 1 if (maxh - SPLASH_Y_OFFSET) % 2 else maxh
    maxw = maxw - 1 if (maxw - BORDER_X_OFFSET) % 2 else maxw

    screen.move(SPLASH_Y_OFFSET, 1)
    screen.clrtobot()
    screen.addstr(y, maxw//2 - len(option), option)
    screen.addstr(y+3, maxw//2 - len(tooltip)//2, tooltip)
    editwin = curses.newwin(1, maxChar, y, x)
    rectangle(screen, y-1, x-2, y-1+1+1, x+maxChar+1)
    screen.refresh()
    box = Textbox(editwin)
    # Let the user edit until Ctrl-G is struck. (or Enter)
    box.edit()
    # Get resulting contents
    new_val = box.gather()
    del box
    del editwin
    return new_val


def valid_sizes(s, max):
    MIN = 5
    s = int(s.strip(" "))
    if s % 2 == 0:
        raise ValueError
    if MIN <= s <= max:
        return s
    else:
        raise ValueError


def valid_gen_speed(s):
    MIN = 1
    MAX = 1000
    s = int(s.strip(" "))
    if MIN <= s <= MAX:
        return s
    else:
        raise ValueError


def valid_seed(s):
    s = int(s.strip(" "))
    if 0 <= s <= 99999:
        return s
    else:
        raise ValueError


def player_at_exit(x, y, exitPos):
    return (x, y) == exitPos


def is_winner(screen):
    screen.move(SPLASH_Y_OFFSET, BORDER_X_OFFSET)
    screen.clrtobot()
    WIN = []
    WIN_TXT = ["", "Congrats, you've escaped the maze!",
               "Press Q to quit, S to do a new maze, or O for options"]
    for txt in WIN_TXT:
        WIN.append(txt.center(curses.COLS - 2, " "))
    for y in range(len(WIN)):
        for x in range(len(WIN[y])):
            if WIN[y][x] == " ":
                continue
            # We lazily skip over drawing any blank characters for now.
            screen.addch(y+SPLASH_Y_OFFSET, x+BORDER_X_OFFSET, WIN[y][x])
            screen.refresh()


if __name__ == "__main__":
    # Wrapper handles exceptions much more cleanly than doing things yourself with try...except...
    # It also initializes: cbreak, noecho, keypad TRUE, and colors, restores it all itself on exit as well.
    curses.wrapper(main)

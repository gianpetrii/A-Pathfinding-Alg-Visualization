import pygame
import math
from queue import PriorityQueue

# DISPLAY SIZE
WIDTH = 700
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

# COLOURS THAT WILL BE USED DURING ANIMATION
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


# DEF CLASS FOR A SINGLE CUBE
class Cube:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width  # position on screen
        self.y = col * width  # position on screen
        self.color = WHITE  # starting color for all cubes
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    """THE NEXT DEFs TELLS THE POSITION AND STATE OF EACH CUBE"""

    def get_pos(self):  # used to get position of each cube
        return self.row, self.col

    def is_closed(self):  # return means it is already used, not available to go through
        return self.color == RED

    def is_open(self):  # open set
        return self.color == GREEN

    def is_barrier(self):  # it´s a barrier
        return self.color == BLACK

    def is_start(self):  # starting color
        return self.color == ORANGE

    def is_end(self):  # the last cube
        return self.color == TURQUOISE

    def reset(self):  # just to reset the colors
        self.color = WHITE

    """THE NEXT DEFs MAKE THE SWITCH TO A COLOR WHEN CALLED"""

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    # method that draws the cube on the screen
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))  # where to draw, what color, size

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


"""HEURISTIC FUNCTION"""


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {cube: float("inf") for row in grid for cube in row}
    g_score[start] = 0
    f_score = {cube: float("inf") for row in grid for cube in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


"""LIST THAT HOLDS ALL THE SPOTS"""


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            cube = Cube(i, j, gap, rows)  # create each cube, it is a list inside a list
            grid[i].append(cube)

    return grid


"""DRAWS EACH GRID LINE THAT SEPARATES EACH CUBE"""


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))  # draws horizontal all lines
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))  # draws vertical all lines


"""PAINTS EVERYTHING WHITE SO THE NEXT STATE CAN RE-PAINT IT"""


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for cube in row:
            cube.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


"""RETRIEVES THE CLICKED POSITION TO TURN IT BLACK LATTER ON"""


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos  # because its row, collum

    row = y // gap
    col = x // gap

    return row, col


def main(win, width):
    ROWS = 50  # amount of rows
    grid = make_grid(ROWS, width)  # makes the grid

    start = None  # starting position
    end = None  # ending position

    run = True  # keeps track of if its running the loop or not
    started = False  # checks if the AI is resolving it
    while run:
        draw(win, grid, ROWS, width)    #draws everything
        for event in pygame.event.get():  # goes through every event like click or type etc
            if event.type == pygame.QUIT:  # if this event happens it stops and closes the game
                run = False

            if started:  # if started nothign can be changed on the board so as not to click and bug the program
                continue

            """EVERYTHING THAT HAPPENS WHEN YOU CLICK"""
            if pygame.mouse.get_pressed()[0]:  # LEFT CLICK
                pos = pygame.mouse.get_pos()    # gets mouse position on the screen when clicked
                row, col = get_clicked_pos(pos, ROWS, width)  # pass position and return actual cube coordinates
                # clicked on display
                cube = grid[row][col]   # index row, col in the grid of the modifiable cubes
                if not start and cube != end:   # if its first clicked cube then it is the start
                    start = cube
                    start.make_start()

                elif not end and cube != start:     # if the start cube is selected, select the end cube next
                    end = cube
                    end.make_end()

                elif cube != end and cube != start:     # creates barrier since start and end is all done
                    cube.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT CLICK
                pos = pygame.mouse.get_pos()        # gets mouse position in screen
                row, col = get_clicked_pos(pos, ROWS, width)    # returns row and col of cube
                cube = grid[row][col]   # stores cube in list of modifiable cubes
                cube.reset()    # resets cube to white
                if cube == start:
                    start = None
                elif cube == end:
                    end = None

            if event.type == pygame.KEYDOWN:    # did you press a key?
                if event.key == pygame.K_SPACE and start and end:   # was the key pressed the SPACE key?
                    for row in grid:
                        for cube in row:
                            cube.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)

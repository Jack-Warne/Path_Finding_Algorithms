import pygame

import time
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dijkstra's Path Finding Algorithm")


# each colour represents the state of each node, helping determine what set it bleongs to

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255,221,51)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255,140,25)

class Node:
    def __init__ (self, row, col, width, total_rows):
        self.row = row
        self.col = col
        # need to keep track of x/y coordinate because pygame needs to draw a cube rather than just fill
        # and area. This allows us to find the location for each cube as it will be 800 / 50 
        # as it is a 50*50 grid
        self.x = row * width
        self.y = col * width

        self.colour = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows
        
    def get_pos(self): # this returns the position of any given square in the grid
        return self.row, self.col
    
    def is_closed(self): # checks if a node is closed/checked i.e a yellow node in the closed set
        return self.colour == YELLOW
     
    def is_open(self): #checks if current node is in the open set
        return self.colour == ORANGE
    
    def is_barrier(self): # checks if node is checkable
        return self.colour == BLACK
    
    def is_start_node(self): # defines where the search will start from
        return self.colour == GREEN
    
    def is_dest_node(self): # defines where the algorithm is trying to go
        return self.colour == RED
    
    def reset_node(self): # resets a node from any given state back to the default state
        self.colour = WHITE
    
    # these are to actually set the colours rather than just asking to return a colour
    
    def START(self):
        self.colour = GREEN
    
    def CLOSE(self):
        self.colour = YELLOW
    
    def OPEN(self):
        self.colour = ORANGE
    
    def BARRIER(self):
        self.colour = BLACK
    
    def END(self):
        self.colour = RED
       
    def PATH(self):
        self.colour = PURPLE
    
    def draw(self, win): # for pygame 0,0 is the top left hand side of the window
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))
    
    def update_neighbours(self, grid): # adds all valid neighbours to the neigbours list so it doesn't try and traverse through barriers
        # check up down left right and check they are not barriers
        self.neighbours = []
        if self.col < self.total_rows -1 and not grid[self.row][self.col + 1].is_barrier(): # check left
                self.neighbours.append(grid[self.row][self.col + 1])
        
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # check up
            self.neighbours.append(grid[self.row - 1][self.col])
        
        if self.row < self.total_rows - 1 and not grid[self.row][self.col - 1].is_barrier(): # check right
             self.neighbours.append(grid[self.row][self.col-1])
            
        if self.row < self.total_rows -1 and not grid[self.row + 1][self.col].is_barrier(): # check down
            self.neighbours.append(grid[self.row + 1][self.col])
            
    def __lt__ (self, other): # less than function compares two nodes
        return False

# define the heuristic function, defines distance between point1 and point2 and returns it
# using manhatten distance to help guess the nearest distance
def h(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs (y1 - y2) # returns absolute distance of (x1-x2) + (y1-y2), our heuristic

# makes path by iterating from came from and making it part of the path

def reconstruct_path(came_from, current, end, draw):
    while current in came_from:
        current = came_from[current]
        current.PATH()
        
        draw()
        


# Implementation of Dijkstras Algorithm

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start)) # adds start node with its score of 0, count is used to break ties if two nodes have the same score
    came_from = {} # creates a list of where each node came from to make path reconstruction easier
    Q = {node: float("inf") for row in grid for node in row} # sets all nodes to have a score of infinity as the scores are unknown
    Q[start] = 0

    while not open_set.empty():
        for event in pygame.event.get(): # if there is no possible path the user can still quit
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # finding the current node indexing at 2 because we just want the node not the score
        if current == end: # if the end node has been reached reconstruct the path
            reconstruct_path(came_from, current, end, draw)
            end.END()
            return True

        for neighbour in current.neighbours:
            temp_Q = Q[current] + 1

            if temp_Q < Q[neighbour]: # if q score is lower update values to make a better path
                came_from[neighbour] = current
                Q[neighbour] = temp_Q
                open_set.put((Q[neighbour], count, neighbour))
                neighbour.OPEN() # show we have already considered the node
        draw()

        if current != start:
            current.CLOSE()

    return False


           
# create a grid data structure to hold all of the nodes and their respective data

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            if i == 0 or i == rows - 1 or j == 0 or j == rows - 1:
                node = Node(i, j, gap, rows)
                node.BARRIER()  # Set perimeter nodes as barriers
            else:
                node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw(win, grid, rows, width): # function that draws everything that has been set out
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    
    pygame.display.update()
    
def clicked_pos(pos, rows, width):
    gap = width // rows
    y,x = pos
    # this takes the position of x and position of y and finds out where they are and what cube has been clicked using the width of the cubes
    row = y // gap
    col = x // gap
    
    return row, col

# main function to set up events

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    
    start = None
    end = None
    
    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get(): # at begining of while loop runs through all events to check what they are
            if event.type == pygame.QUIT:
                run = False
            if started: # if algorithm has started the user can't change anything i.e. add barriers
                continue
            if pygame.mouse.get_pressed()[0]: # if left mouse clicked
                pos = pygame.mouse.get_pos()
                row, col = clicked_pos(pos, ROWS, width) # gives us the rows and coloumns that has been clicked
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.START()
                elif not end and node != start:
                    end = node
                    end.END()
                elif node != end and node != start:
                    node.BARRIER()
            elif pygame.mouse.get_pressed()[2]: # if right mouse clicked
                pos = pygame.mouse.get_pos()
                row, col = clicked_pos(pos, ROWS, width) # gives us the rows and coloumns that has been clicked
                node = grid[row][col]
                node.reset_node()
                if node == start:
                    start = None
                elif node == end:
                    end = None
            if event.type == pygame.KEYDOWN: # checks to see if a key has been pressed
                if event.key == pygame.K_SPACE and not started: # if the key pressed is spacebar then the algorithm runs
                    start_time = time.time()
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)  # lambda is anonymous function so we can parse draw as an argument to another function
                    end_time = time.time()
                    print(end_time - start_time)
                if event.key == pygame.K_r: # reset grid when user presses r
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()
    
main(WIN, WIDTH)
    

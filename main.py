import pygame
import settings
import time
from algorithms import bfs, dfs, astar, hill_climbing

# --- MAZE GENERATION ---
try:
    from mazelib import Maze
    from mazelib.generate.Prims import Prims
except ImportError:
    print("Error: mazelib not found. Run: pip install mazelib")
    exit()

pygame.init()
pygame.font.init()

# Setup Screen
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Maze Pathfinding Visualizer")
font = pygame.font.SysFont('Arial', 24, bold=True)
menu_font = pygame.font.SysFont('Arial', 30, bold=True) # Slightly larger for menu title

# ---------------------------------------------------------
# GRID CREATION
# ---------------------------------------------------------
def create_empty_grid():
    return [[0 for _ in range(settings.COLS)] for _ in range(settings.ROWS)]

# ---------------------------------------------------------
# MAZELIB GENERATOR
# ---------------------------------------------------------
def generate_mazelib_grid():
    r = (settings.ROWS - 1) // 2    # mazelib requires odd dimensions
    c = (settings.COLS - 1) // 2
    m = Maze()
    m.generator = Prims(r, c)
    m.generate()
    # mazelib gives 0 = path, 1 = wall
    new_grid = [row[:] for row in m.grid.tolist()]
    start = (1, 1)
    end = (len(new_grid) - 2, len(new_grid[0]) - 2)
    return new_grid, start, end

grid = create_empty_grid()
start = None
end = None
timer_text = ""
game_state = "MENU"  # NEW: Tracks if we are in MENU or RUNNING mode

# ---------------------------------------------------------
# DRAW FUNCTIONS
# ---------------------------------------------------------
def draw_menu():
    screen.fill(settings.WHITE)
    
    # Title
    title = menu_font.render("CONTROLS", True, settings.BLUE)
    screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, 40))

    # List of controls
    controls = [
        "Left Click: Set Start / End / Walls",
        "Right Click: Erase",
        "M: Generate Maze",
        "C: Clear Grid",
        "B: Run BFS",
        "D: Run DFS",
        "A: Run A-Star",
        "H: Run Hill Climbing",
        "ESC: Back to Menu",
        "",
        "PRESS SPACE TO START"
    ]

    y_offset = 100
    for line in controls:
        if line == "PRESS SPACE TO START":
            color = settings.GREEN
        else:
            color = settings.BLACK
            
        text = font.render(line, True, color)
        screen.blit(text, (settings.WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 40
    
    pygame.display.update()

def draw_grid():
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            color = settings.WHITE
            if grid[r][c] == 1: color = settings.BLACK
            if (r, c) == start: color = settings.GREEN
            if (r, c) == end: color = settings.RED
            pygame.draw.rect(screen, color,
                             (c * settings.CELL_SIZE, r * settings.CELL_SIZE,
                              settings.CELL_SIZE, settings.CELL_SIZE))
            pygame.draw.rect(screen, settings.GRAY,
                             (c * settings.CELL_SIZE, r * settings.CELL_SIZE,
                              settings.CELL_SIZE, settings.CELL_SIZE), 1)

def draw_step(pos, state):
    r, c = pos
    if (r, c) == start or (r, c) == end:
        return

    color = settings.BLUE if state == "open" else settings.YELLOW
    pygame.draw.rect(screen, color,
                     (c * settings.CELL_SIZE, r * settings.CELL_SIZE,
                      settings.CELL_SIZE, settings.CELL_SIZE))
    pygame.display.update()
    pygame.time.delay(10)

def draw_path(path):
    for r, c in path:
        if (r, c) == start or (r, c) == end:
            continue
        pygame.draw.rect(screen, settings.YELLOW,
                         (c * settings.CELL_SIZE, r * settings.CELL_SIZE,
                          settings.CELL_SIZE, settings.CELL_SIZE))
        pygame.display.update()
        pygame.time.delay(20)

def draw_timer():
    if timer_text:
        surf = font.render(timer_text, True, settings.RED)
        bg = surf.get_rect(topleft=(10, 10))
        bg.inflate_ip(10, 10)
        pygame.draw.rect(screen, settings.WHITE, bg)
        pygame.draw.rect(screen, settings.BLACK, bg, 2)
        screen.blit(surf, (10, 10))

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------

run = True
while run:
    
    # --- MENU STATE ---
    if game_state == "MENU":
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = "RUNNING"
                    screen.fill(settings.WHITE) # Clean wipe before showing grid

    # --- RUNNING STATE ---
    elif game_state == "RUNNING":
        screen.fill(settings.WHITE)
        draw_grid()
        draw_timer()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # MOUSE CONTROLS
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                r, c = y // settings.CELL_SIZE, x // settings.CELL_SIZE
                if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                    if not start: start = (r, c)
                    elif not end: end = (r, c)
                    else: grid[r][c] = 1
            if pygame.mouse.get_pressed()[2]:
                x, y = pygame.mouse.get_pos()
                r, c = y // settings.CELL_SIZE, x // settings.CELL_SIZE
                if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                    grid[r][c] = 0
                    if start == (r, c): start = None
                    if end == (r, c): end = None

            # KEY CONTROLS
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_ESCAPE: # GO BACK TO MENU
                    game_state = "MENU"

                if event.key == pygame.K_m:   # MAZE GENERATE
                    grid, start, end = generate_mazelib_grid()
                    timer_text = ""

                if event.key == pygame.K_c:   # CLEAR GRID
                    grid = create_empty_grid()
                    start = None
                    end = None
                    timer_text = ""

                # RUN ANY ALGO
                if start and end:
                    def run_algo(name, func):
                        global timer_text
                        t1 = time.time()
                        path = func(grid, start, end, draw_step)
                        t2 = time.time()
                        timer_text = f"{name}: {t2 - t1:.2f} sec"
                        if path:
                            draw_path(path)
                    
                    if event.key == pygame.K_b: run_algo("BFS", bfs)
                    if event.key == pygame.K_d: run_algo("DFS", dfs)
                    if event.key == pygame.K_a: run_algo("A-Star", astar)
                    if event.key == pygame.K_h: run_algo("Hill Climbing", hill_climbing)

pygame.quit()
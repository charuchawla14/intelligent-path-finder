import pygame
import pickle
import networkx as nx
from main import grid, generate_signals, heuristic, get_weight_ml

def run_animation(grid, path, signal_map, G):

    pygame.init()

    CELL_SIZE = 70
    rows = len(grid)
    cols = len(grid[0])

    WIDTH = cols * CELL_SIZE
    HEIGHT = rows * CELL_SIZE + 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Intelligent Traffic System 🚗")

    font_small = pygame.font.SysFont("Arial", 16)
    font_time = pygame.font.SysFont("Arial", 28)

    WHITE = (255,255,255)
    BLACK = (0,0,0)
    GREEN = (0,200,0)
    RED = (200,0,0)
    LIGHT_BLUE = (173,216,230)
    YELLOW = (255,255,0)
    GRAY = (200,200,200)
    ORANGE = (255,165,0)
    PURPLE = (128,0,128)

    clock = pygame.time.Clock()

    def draw_grid():
        for r in range(rows):
            for c in range(cols):

                x = c * CELL_SIZE
                y = r * CELL_SIZE

                cell = grid[r][c]
                color = WHITE
                label = ""

                if cell == 'X':
                    color = BLACK
                elif cell == 'A':
                    color = GREEN
                    label = "A"
                elif cell == 'B':
                    color = RED
                    label = "B"
                elif cell == 'S':
                    color = ORANGE
                    label = "S"
                elif cell == 'M':
                    color = PURPLE
                    label = "M"
                elif cell == 'T':
                    sig = signal_map[(r,c)]

                    if sig == "red":
                        color = (200,40,40)
                    elif sig == "yellow":
                        color = YELLOW
                    else:
                        color = (120,255,120)

                    label = "🚦"

                pygame.draw.rect(screen, color, (x,y,CELL_SIZE,CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (x,y,CELL_SIZE,CELL_SIZE), 1)

                if label:
                    text = font_small.render(label, True, BLACK)
                    text_rect = text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
                    screen.blit(text, text_rect)

    def draw_path(upto):
        for i in range(upto + 1):
            r, c = path[i]
            pygame.draw.rect(
                screen,
                LIGHT_BLUE,
                (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )

    def draw_car(r, c):
        x = c * CELL_SIZE
        y = r * CELL_SIZE

        pygame.draw.rect(screen, (0,0,0), (x+10, y+25, 50, 25))
        pygame.draw.rect(screen, (0,150,255), (x+15, y+30, 40, 15))

        pygame.draw.circle(screen, BLACK, (x+15, y+55), 5)
        pygame.draw.circle(screen, BLACK, (x+55, y+55), 5)

    def animate():
        total_time = 0

        for i in range(len(path)):

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            r, c = path[i]

            screen.fill(WHITE)

            draw_grid()
            draw_path(i)
            draw_car(r, c)

            if i > 0:
                prev = path[i-1]
                curr = path[i]
                total_time += G[prev][curr]['weight']

            time_text = font_time.render(
                f"Time: {round(total_time,2)} sec",
                True,
                BLACK
            )
            screen.blit(time_text, (10, HEIGHT - 50))

            pygame.display.update()
            pygame.time.delay(120)

    running = True
    while running:
        animate()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(10)

    pygame.quit()


if __name__ == "__main__":

    print("🎬 Running animation...")

    
    with open("path_data.pkl", "rb") as f:
        path, total_time = pickle.load(f)

    
    signal_map = generate_signals()

    G = nx.Graph()
    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] not in ['X','S','M']:
                G.add_node((r,c))

                for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nr, nc = r+dr, c+dc

                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] not in ['X','S','M']:
                            weight = get_weight_ml(grid[nr][nc], nr, nc, signal_map)
                            G.add_edge((r,c),(nr,nc), weight=weight)

    run_animation(grid, path, signal_map, G)
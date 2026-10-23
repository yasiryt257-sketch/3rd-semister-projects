
import pygame
import random
import json
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
CELL = 20
HUD = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON SNAKE")
clock = pygame.time.Clock()

BG = (10, 15, 30)
GRID = (25, 35, 55)
GREEN = (50, 255, 120)
RED = (255, 65, 90)
GOLD = (255, 210, 65)
CYAN = (50, 220, 255)
WHITE = (240, 245, 255)

font = pygame.font.SysFont("consolas", 22, bold=True)
big = pygame.font.SysFont("consolas", 48, bold=True)
small = pygame.font.SysFont("consolas", 16)

COLS = WIDTH // CELL
ROWS = (HEIGHT - HUD) // CELL
SAVE = "snake_highscore.json"

try:
    with open(SAVE) as f:
        best = json.load(f).get("best", 0)
except (OSError, ValueError, TypeError):
    best = 0

def draw_text(msg, fnt, color, x, y):
    img = fnt.render(str(msg), True, color)
    screen.blit(img, img.get_rect(center=(x, y)))

def save_score():
    global best
    if score > best:
        best = score
        try:
            with open(SAVE, "w") as f:
                json.dump({"best": best}, f)
        except OSError:
            pass

def spawn(occupied):
    free = [(x, y) for x in range(COLS)
            for y in range(ROWS) if (x, y) not in occupied]
    return random.choice(free) if free else None

def new_game():
    global snake, direction, next_dir, food, bonus
    global score, level, state, timer, shield, powerup, power_timer

    x, y = COLS // 2, ROWS // 2
    snake = [(x, y), (x-1, y), (x-2, y)]
    direction = (1, 0)
    next_dir = (1, 0)
    score = 0
    level = 1
    timer = 0
    shield = False
    powerup = None
    power_timer = 0
    bonus = None
    food = spawn(set(snake))
    state = "playing"

def end_game():
    global state
    save_score()
    state = "over"

def move_snake():
    global direction, next_dir, food, bonus
    global score, level, shield, powerup, power_timer

    direction = next_dir
    hx, hy = snake[0]
    head = (hx + direction[0], hy + direction[1])

    if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
        end_game()
        return

    growing = head == food or head == bonus
    body = snake if growing else snake[:-1]

    if head in body:
        if shield:
            shield = False
            return
        end_game()
        return

    snake.insert(0, head)

    if head == food:
        score += 10
        food = spawn(set(snake))
        if score % 50 == 0 and bonus is None:
            bonus = spawn(set(snake))
        if powerup is None and random.random() < 0.2:
            pos = spawn(set(snake) | ({bonus} if bonus else set()))
            if pos:
                powerup = (pos, random.choice(["shield", "boost"]))

    elif head == bonus:
        score += 50
        bonus = None
    else:
        snake.pop()

    if powerup and head == powerup[0]:
        if powerup[1] == "shield":
            shield = True
        else:
            power_timer = 4000
        powerup = None

    level = 1 + score // 100

def draw_game():
    screen.fill(BG)

    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRID, (x, HUD), (x, HEIGHT))
    for y in range(HUD, HEIGHT, CELL):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

    pygame.draw.rect(screen, (18, 26, 45), (0, 0, WIDTH, HUD))
    pygame.draw.line(screen, CYAN, (0, HUD), (WIDTH, HUD), 2)

    draw_text(f"SCORE: {score}", font, GREEN, 90, 20)
    draw_text(f"BEST: {best}", font, GOLD, 260, 20)
    draw_text(f"LEVEL: {level}", font, CYAN, 440, 20)
    draw_text("SHIELD" if shield else "", small, CYAN, 680, 20)

    if food:
        r = pygame.Rect(food[0]*CELL+3, HUD+food[1]*CELL+3,
                        CELL-6, CELL-6)
        pygame.draw.ellipse(screen, RED, r)

    if bonus:
        r = pygame.Rect(bonus[0]*CELL+2, HUD+bonus[1]*CELL+2,
                        CELL-4, CELL-4)
        pygame.draw.rect(screen, GOLD, r, border_radius=5)

    if powerup:
        pos, kind = powerup
        color = CYAN if kind == "shield" else (190, 90, 255)
        pygame.draw.circle(screen, color,
                           (pos[0]*CELL+10, HUD+pos[1]*CELL+10), 8)

    for i, (x, y) in enumerate(snake):
        r = pygame.Rect(x*CELL+1, HUD+y*CELL+1, CELL-2, CELL-2)
        color = (150, 255, 180) if i == 0 else (
            30, max(100, 240-i), 100)
        pygame.draw.rect(screen, color, r, border_radius=5)

    if state == "paused":
        draw_text("PAUSED", big, GOLD, WIDTH//2, HEIGHT//2)
        draw_text("Press P to resume", font, WHITE,
                  WIDTH//2, HEIGHT//2+55)

    if state == "over":
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 190))
        screen.blit(shade, (0, 0))
        draw_text("GAME OVER", big, RED, WIDTH//2, HEIGHT//2-45)
        draw_text(f"Score: {score}  Best: {best}",
                  font, WHITE, WIDTH//2, HEIGHT//2+10)
        draw_text("ENTER: Play again   ESC: Quit",
                  small, GOLD, WIDTH//2, HEIGHT//2+55)

state = "menu"
running = True
snake = []
score = 0
level = 1
timer = 0

while running:
    dt = clock.tick(60)
    timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score()
            running = False

        elif event.type == pygame.KEYDOWN:
            k = event.key

            if state == "menu":
                if k in (pygame.K_RETURN, pygame.K_SPACE):
                    new_game()
                elif k == pygame.K_ESCAPE:
                    running = False

            elif state == "over":
                if k == pygame.K_RETURN:
                    new_game()
                elif k == pygame.K_ESCAPE:
                    running = False

            elif state == "playing":
                if k == pygame.K_p:
                    state = "paused"
                elif k == pygame.K_r:
                    new_game()
                elif k in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    next_dir = (0, -1)
                elif k in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    next_dir = (0, 1)
                elif k in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    next_dir = (-1, 0)
                elif k in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    next_dir = (1, 0)

            elif state == "paused":
                if k == pygame.K_p:
                    state = "playing"
                elif k == pygame.K_r:
                    new_game()
                elif k == pygame.K_ESCAPE:
                    state = "menu"

    if state == "menu":
        screen.fill(BG)
        draw_text("NEON SNAKE", big, GREEN, WIDTH//2, 170)
        draw_text("Eat food. Grow longer. Beat your record!",
                  font, WHITE, WIDTH//2, 250)
        draw_text("Arrow keys / WASD: Move", small, CYAN,
                  WIDTH//2, 320)
        draw_text("P: Pause    R: Restart", small, WHITE,
                  WIDTH//2, 350)
        draw_text("ENTER: START GAME", font, GOLD,
                  WIDTH//2, 420)
        draw_text(f"PERSONAL BEST: {best}", font, CYAN,
                  WIDTH//2, 485)

    else:
        if state == "playing":
            power_timer = max(0, power_timer-dt)
            speed = min(22, 8+level-1)
            if power_timer > 0:
                speed = min(28, speed+7)

            if bonus and random.random() < dt / 6000:
                bonus = None

            if timer >= 1000/speed:
                timer = 0
                move_snake()

        draw_game()

    pygame.display.flip()

pygame.quit()

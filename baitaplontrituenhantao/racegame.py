import pygame
import random
import time
import heapq

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 700
CELL_SIZE = 60
MAP_WIDTH, MAP_HEIGHT = SCREEN_WIDTH // CELL_SIZE, (SCREEN_HEIGHT - 100) // CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 204)
HOVER_BLUE = (0, 153, 255)
RED = (255, 0, 0)

background_menu = pygame.image.load("background.jpg")
background_menu = pygame.transform.scale(background_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))

hover_sound = pygame.mixer.Sound("click-21156.mp3")
click_sound = pygame.mixer.Sound("click-21156.mp3")

FONT = pygame.font.SysFont("arial", 50)
SMALL_FONT = pygame.font.SysFont("arial", 30)

car_images = ["car02.jpg", "car03.jpg", "car04.jpg"]
obstacle_images = {
    "water": pygame.image.load("water.jpg"),
    "mud": pygame.image.load("mud.jpg"),
    "trap": pygame.image.load("trap.jpg"),
    "rock": pygame.image.load("rock.jpg")
}
skill_image = pygame.image.load("skill.jpg")
flag_img = pygame.transform.scale(pygame.image.load("flag.png"), (CELL_SIZE, CELL_SIZE))

START = (0, 0)
GOAL = (MAP_WIDTH - 1, MAP_HEIGHT - 1)

selected_car_index = 0
car_img = pygame.transform.scale(pygame.image.load(car_images[selected_car_index]), (CELL_SIZE, CELL_SIZE))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Đua xe A*")

def draw_button(x, y, width, height, text, font, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    is_hover = x < mouse[0] < x + width and y < mouse[1] < y + height

    button_color = hover_color if is_hover else color
    pygame.draw.rect(screen, button_color, (x, y, width, height), border_radius=15)

    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2,
                               y + (height - text_surface.get_height()) // 2))

    if is_hover and click[0]:
        click_sound.play()
        time.sleep(0.2)
        return True
    return False

def a_star_search(start, goal, grid):
    open_list = []
    closed_list = set()
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    heapq.heappush(open_list, (f_score[start], start))

    while open_list:
        current_f, current = heapq.heappop(open_list)
        if current == goal:
            path = reconstruct_path(came_from, current)
            return path

        closed_list.add(current)

        for neighbor in neighbors(current, grid):
            if neighbor in closed_list:
                continue

            tentative_g_score = g_score[current] + movement_cost(grid[neighbor[1]][neighbor[0]])

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)

                if neighbor not in open_list:
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []  # Không có đường đi hợp lệ

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(position, grid):
    x, y = position
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and grid[ny][nx] != "rock":
            neighbors.append((nx, ny))
    return neighbors

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def movement_cost(cell):
    if cell == "water":
        return 2  # Tăng chi phí di chuyển qua nước
    elif cell == "mud":
        return 3  # Tăng chi phí di chuyển qua bùn
    elif cell == "trap":
        return 5  # Tăng chi phí di chuyển qua bẫy
    return 1  # Chi phí mặc định

def generate_map():
    grid = [["empty" for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    path = []
    x, y = START

    while (x, y) != GOAL:
        path.append((x, y))
        if x < GOAL[0] and (random.random() < 0.5 or y == GOAL[1]):
            x += 1
        elif y < GOAL[1]:
            y += 1
    path.append(GOAL)

    for _ in range(200):
        x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
        if (x, y) not in path and (x, y) != START and (x, y) != GOAL:
            grid[y][x] = random.choices(["water", "mud", "trap", "rock"], weights=[1, 1, 1, 3])[0]

    skill_count = random.randint(1, 2)
    while skill_count > 0:
        x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
        if grid[y][x] == "empty" and (x, y) not in path and (x, y) != START and (x, y) != GOAL:
            grid[y][x] = "skill"
            skill_count -= 1

    return grid

def main_menu():
    title_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
    color_index = 0
    color_change_time = time.time()

    while True:
        screen.blit(background_menu, (0, 0))

        if time.time() - color_change_time > 0.5:
            color_index = (color_index + 1) % len(title_colors)
            color_change_time = time.time()

        title_text = FONT.render(" GAME ĐUA XE ", True, title_colors[color_index])
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        if draw_button(SCREEN_WIDTH // 2 - 100, 250, 200, 60, "Choi", SMALL_FONT, BLUE, HOVER_BLUE):
            choose_car()
        if draw_button(SCREEN_WIDTH // 2 - 100, 350, 200, 60, "Huong Dan", SMALL_FONT, BLUE, HOVER_BLUE):
            show_instructions()
        if draw_button(SCREEN_WIDTH // 2 - 100, 450, 200, 60, "Thoat", SMALL_FONT, BLUE, HOVER_BLUE):
            pygame.quit()
            exit()

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def show_instructions():
    running = True
    while running:
        screen.fill(LIGHT_GRAY)
        texts = [
            "- Di chuyen xe bang phim mui ten.",
            "- Tranh chuong ngai vat:",
            "  + Nuoc: di cham.",
            "  + Bun: co nguy co truot.",
            "  + Bay: quay ve vi tri xuat phat.",
            "- An ky nang de di qua 1 chuong ngai vat bat ky (1 lan)."
        ]
        for i, line in enumerate(texts):
            screen.blit(FONT.render(line, True, BLACK), (50, 100 + i * 50))

        back_button = pygame.Rect(50, 500, 200, 50)
        pygame.draw.rect(screen, BLUE, back_button, border_radius=10)
        screen.blit(FONT.render("Tro lai", True, WHITE), (back_button.x + 40, back_button.y + 10))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    click_sound.play()
                    time.sleep(0.2)
                    running = False

LIGHT_GRAY = (230, 230, 230)
HIGHLIGHT_COLOR = (255, 200, 0)

def choose_car():
    global selected_car_index, car_img
    running = True
    CAR_DISPLAY_SIZE = (100, 60)
    background_color = (200, 220, 255)
    HIGHLIGHT_COLOR = (100, 200, 255)

    while running:
        screen.fill(background_color)
        screen.blit(FONT.render("Chon xe:", True, BLACK), (50, 50))

        mouse_pos = pygame.mouse.get_pos()

        for i, path in enumerate(car_images):
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, CAR_DISPLAY_SIZE)
            rect = pygame.Rect(50 + i * 150, 150, CAR_DISPLAY_SIZE[0], CAR_DISPLAY_SIZE[1])

            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect.inflate(10, 10), border_radius=8)

            if i == selected_car_index:
                pygame.draw.rect(screen, RED, rect.inflate(12, 12), 4, border_radius=10)

            screen.blit(img, rect.topleft)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(car_images)):
                    rect = pygame.Rect(50 + i * 150, 150, CAR_DISPLAY_SIZE[0], CAR_DISPLAY_SIZE[1])
                    if rect.collidepoint(event.pos):
                        selected_car_index = i
                        hover_sound.play()
                        car_img = pygame.transform.scale(
                            pygame.image.load(car_images[selected_car_index]), 
                            (CELL_SIZE, CELL_SIZE)
                        )
                        running = False
                        start_game()

def start_game():
    global MAP, car_img  
    MAP = generate_map()
    car_pos = list(START)
    skill_available = 0
    start_time = time.time()

    path = a_star_search(START, GOAL, MAP)
    path_set = set(path)
    visited_cells = set()

    score = 0
    first_move = True

    show_path_time = 2
    path_start_time = time.time()

    running = True
    while running:
        screen.fill(WHITE)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                cell = MAP[y][x]
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell in obstacle_images:
                    img = pygame.transform.scale(obstacle_images[cell], (CELL_SIZE, CELL_SIZE))
                    screen.blit(img, rect)
                elif cell == "skill":
                    img = pygame.transform.scale(skill_image, (CELL_SIZE, CELL_SIZE))
                    screen.blit(img, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        if time.time() - path_start_time < show_path_time:
            for (x, y) in path:
                pygame.draw.rect(screen, (0, 255, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

        screen.blit(car_img, (car_pos[0] * CELL_SIZE, car_pos[1] * CELL_SIZE))
        screen.blit(flag_img, (GOAL[0] * CELL_SIZE, GOAL[1] * CELL_SIZE))

        elapsed_time = int(time.time() - start_time)
        score_text = SMALL_FONT.render(f"Điểm: {score}", True, BLACK)
        time_text = SMALL_FONT.render(f"Thời gian: {elapsed_time}s", True, BLACK)
        screen.blit(score_text, (20, SCREEN_HEIGHT - 80))
        screen.blit(time_text, (20, SCREEN_HEIGHT - 50))

        current_cell = tuple(car_pos)
        if current_cell not in visited_cells:
            if current_cell in path_set:
                score += 10
            else:
                score = max(0, score - 5)
            visited_cells.add(current_cell)

        if tuple(car_pos) == GOAL:
            total_time = int(time.time() - start_time)
            show_finish(total_time, score, skill_available)
            return

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT: dx = -1
                if event.key == pygame.K_RIGHT: dx = 1
                if event.key == pygame.K_UP: dy = -1
                if event.key == pygame.K_DOWN: dy = 1
                nx, ny = car_pos[0] + dx, car_pos[1] + dy

                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    cell = MAP[ny][nx]

                    if cell == "rock":
                        continue

                    if cell == "water":
                        time.sleep(0.5)

                    if cell == "mud":
                        if random.random() < 0.3:
                            continue  

                    if cell == "trap":
                        car_pos = list(START)
                        score = max(0, score - 50)
                        continue  

                    if cell == "skill":
                        skill_available += 1
                        MAP[ny][nx] = "empty"

                    car_pos = [nx, ny]
                    first_move = False

def show_finish(total_time, score, skill_used):
    while True:
        screen.fill(WHITE)

        texts = [
            "🎉 CHUC MUNG BAN DA VE DICH!",
            f"Thoi gian hoan thanh: {total_time}s",
            f"Diem so: {score}",
            f"Ky nang: {skill_used}",
        ]
        for i, line in enumerate(texts):
            text_surface = FONT.render(line, True, BLACK)
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, 150 + i * 60))

        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 60)
        pygame.draw.rect(screen, BLUE, back_button, border_radius=10)
        back_text = FONT.render("Trở lại menu", True, WHITE)
        screen.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2, back_button.y + 10))

        play_again_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 60)
        pygame.draw.rect(screen, BLUE, play_again_button, border_radius=10)
        play_again_text = FONT.render("Chơi lại", True, WHITE)
        screen.blit(play_again_text, (play_again_button.x + (play_again_button.width - play_again_text.get_width()) // 2, play_again_button.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return
                if play_again_button.collidepoint(event.pos):
                    start_game()
                    return

if __name__ == "__main__":
    main_menu()
import math
import random
import sys
from functools import lru_cache

import pygame

pygame.init()

WIDTH = 620
HEIGHT = 720
BOARD_SIZE = 4
CELL_SIZE = 125
GAP = 12
BOARD_X = 42
BOARD_Y = 190
BACKGROUND = (250, 248, 239)
BOARD_BACKGROUND = (187, 173, 160)
TEXT_COLOR = (119, 110, 101)
WHITE = (255, 255, 255)
DARK = (60, 58, 50)

TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 - AI Solver")
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)
TILE_FONT = pygame.font.SysFont("arial", 37, bold=True)
INFO_FONT = pygame.font.SysFont("arial", 21)
BUTTON_FONT = pygame.font.SysFont("arial", 20, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 16)

DIRECTIONS = ("left", "up", "right", "down")
DIRECTION_KEYS = {
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
    pygame.K_DOWN: "down",
    pygame.K_s: "down"
}


def new_board():
    return tuple(tuple(0 for _ in range(BOARD_SIZE)) for _ in range(BOARD_SIZE))


def add_random_tile(board):
    empty = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if board[r][c] == 0
    ]

    if not empty:
        return board

    r, c = random.choice(empty)
    mutable = [list(row) for row in board]
    mutable[r][c] = 4 if random.random() < 0.1 else 2
    return tuple(tuple(row) for row in mutable)


def compress_and_merge(line):
    values = [value for value in line if value != 0]
    result = []
    gained = 0
    index = 0

    while index < len(values):
        if index + 1 < len(values) and values[index] == values[index + 1]:
            merged = values[index] * 2
            result.append(merged)
            gained += merged
            index += 2
        else:
            result.append(values[index])
            index += 1

    result.extend([0] * (BOARD_SIZE - len(result)))
    return result, gained


def move_board(board, direction):
    mutable = [list(row) for row in board]
    total_gain = 0

    if direction == "left":
        for r in range(BOARD_SIZE):
            mutable[r], gained = compress_and_merge(mutable[r])
            total_gain += gained

    elif direction == "right":
        for r in range(BOARD_SIZE):
            reversed_line, gained = compress_and_merge(mutable[r][::-1])
            mutable[r] = reversed_line[::-1]
            total_gain += gained

    elif direction == "up":
        for c in range(BOARD_SIZE):
            line = [mutable[r][c] for r in range(BOARD_SIZE)]
            merged, gained = compress_and_merge(line)
            total_gain += gained
            for r in range(BOARD_SIZE):
                mutable[r][c] = merged[r]

    elif direction == "down":
        for c in range(BOARD_SIZE):
            line = [mutable[r][c] for r in range(BOARD_SIZE - 1, -1, -1)]
            merged, gained = compress_and_merge(line)
            total_gain += gained
            for index, r in enumerate(range(BOARD_SIZE - 1, -1, -1)):
                mutable[r][c] = merged[index]

    result = tuple(tuple(row) for row in mutable)
    if result == board:
        return board, 0

    return result, total_gain


def available_moves(board):
    moves = []
    for direction in DIRECTIONS:
        next_board, _ = move_board(board, direction)
        if next_board != board:
            moves.append(direction)
    return moves


def board_heuristic(board):
    values = [
        [math.log2(value) if value else 0 for value in row]
        for row in board
    ]

    empty_count = sum(value == 0 for row in board for value in row)
    max_tile = max(max(row) for row in board)
    max_log = math.log2(max_tile) if max_tile else 0

    smoothness = 0
    monotonicity = 0
    merge_potential = 0

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            current = values[r][c]
            if current == 0:
                continue

            for nr, nc in ((r + 1, c), (r, c + 1)):
                if nr < BOARD_SIZE and nc < BOARD_SIZE:
                    neighbor = values[nr][nc]
                    if neighbor != 0:
                        smoothness -= abs(current - neighbor)

            if c + 1 < BOARD_SIZE and board[r][c] == board[r][c + 1] and board[r][c] != 0:
                merge_potential += values[r][c]

            if r + 1 < BOARD_SIZE and board[r][c] == board[r + 1][c] and board[r][c] != 0:
                merge_potential += values[r][c]

    for line in values:
        for index in range(BOARD_SIZE - 1):
            if line[index] > line[index + 1]:
                monotonicity += line[index + 1] - line[index]
            else:
                monotonicity += line[index] - line[index + 1]

    for c in range(BOARD_SIZE):
        line = [values[r][c] for r in range(BOARD_SIZE)]
        for index in range(BOARD_SIZE - 1):
            if line[index] > line[index + 1]:
                monotonicity += line[index + 1] - line[index]
            else:
                monotonicity += line[index] - line[index + 1]

    corner_bonus = 0
    corners = (
        board[0][0],
        board[0][BOARD_SIZE - 1],
        board[BOARD_SIZE - 1][0],
        board[BOARD_SIZE - 1][BOARD_SIZE - 1]
    )

    if max_tile in corners:
        corner_bonus = max_log * 2.5

    return (
        empty_count * 270
        + smoothness * 18
        + monotonicity * 8
        + merge_potential * 32
        + max_log * 14
        + corner_bonus
    )


def expectimax(board, depth, is_chance_node):
    if depth == 0 or not available_moves(board):
        return board_heuristic(board)

    if not is_chance_node:
        best_value = float("-inf")

        for direction in DIRECTIONS:
            next_board, _ = move_board(board, direction)
            if next_board == board:
                continue

            value = expectimax(next_board, depth - 1, True)
            best_value = max(best_value, value)

        return best_value

    empty_cells = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if board[r][c] == 0
    ]

    if not empty_cells:
        return expectimax(board, depth - 1, False)

    total_value = 0
    mutable = [list(row) for row in board]
    cell_probability = 1.0 / len(empty_cells)

    for r, c in empty_cells:
        mutable[r][c] = 2
        board_with_two = tuple(tuple(row) for row in mutable)
        total_value += 0.9 * cell_probability * expectimax(
            board_with_two, depth - 1, False
        )

        mutable[r][c] = 4
        board_with_four = tuple(tuple(row) for row in mutable)
        total_value += 0.1 * cell_probability * expectimax(
            board_with_four, depth - 1, False
        )

        mutable[r][c] = 0

    return total_value


def choose_best_move(board, depth=3):
    best_direction = None
    best_value = float("-inf")

    for direction in DIRECTIONS:
        next_board, _ = move_board(board, direction)
        if next_board == board:
            continue

        value = expectimax(next_board, depth - 1, True)

        if value > best_value:
            best_value = value
            best_direction = direction

    return best_direction, best_value


class Game2048:
    def __init__(self):
        self.reset()

    def reset(self):
        board = new_board()
        board = add_random_tile(board)
        board = add_random_tile(board)
        self.board = board
        self.score = 0
        self.best_tile = 2
        self.last_move = "None"
        self.ai_running = False
        self.game_over = False
        self.won = False
        self.ai_depth = 3
        self.move_count = 0

    def play(self, direction):
        if self.game_over or self.won:
            return False

        next_board, gained = move_board(self.board, direction)

        if next_board == self.board:
            return False

        self.board = add_random_tile(next_board)
        self.score += gained
        self.move_count += 1
        self.last_move = direction.upper()
        self.best_tile = max(max(row) for row in self.board)

        if self.best_tile >= 2048:
            self.won = True
            self.ai_running = False
        elif not available_moves(self.board):
            self.game_over = True
            self.ai_running = False

        return True

    def ai_step(self):
        if self.game_over or self.won:
            self.ai_running = False
            return

        direction, _ = choose_best_move(self.board, self.ai_depth)

        if direction is None:
            self.game_over = True
            self.ai_running = False
            return

        self.play(direction)


def draw_button(rect, label, active=False):
    color = (119, 110, 101) if active else (143, 122, 102)
    pygame.draw.rect(screen, color, rect, border_radius=7)
    text = BUTTON_FONT.render(label, True, WHITE)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_game(game):
    screen.fill(BACKGROUND)

    title = TITLE_FONT.render("2048 AI Solver", True, TEXT_COLOR)
    screen.blit(title, (BOARD_X, 28))

    score_label = INFO_FONT.render("SCORE", True, TEXT_COLOR)
    score_value = TITLE_FONT.render(str(game.score), True, TEXT_COLOR)
    screen.blit(score_label, (BOARD_X, 92))
    screen.blit(score_value, (BOARD_X, 115))

    best_label = INFO_FONT.render("BEST TILE", True, TEXT_COLOR)
    best_value = TITLE_FONT.render(str(game.best_tile), True, TEXT_COLOR)
    screen.blit(best_label, (390, 92))
    screen.blit(best_value, (390, 115))

    pygame.draw.rect(
        screen,
        BOARD_BACKGROUND,
        (BOARD_X, BOARD_Y, 536, 536),
        border_radius=10
    )

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            value = game.board[r][c]
            x = BOARD_X + GAP + c * (CELL_SIZE + GAP)
            y = BOARD_Y + GAP + r * (CELL_SIZE + GAP)
            color = TILE_COLORS.get(value, DARK)

            pygame.draw.rect(
                screen,
                color,
                (x, y, CELL_SIZE, CELL_SIZE),
                border_radius=7
            )

            if value:
                text_color = WHITE if value >= 8 else TEXT_COLOR
                font = TILE_FONT if value < 1024 else INFO_FONT
                tile_text = font.render(str(value), True, text_color)
                screen.blit(
                    tile_text,
                    tile_text.get_rect(
                        center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)
                    )
                )

    draw_button(pygame.Rect(42, 625, 155, 42), "Start AI", game.ai_running)
    draw_button(pygame.Rect(207, 625, 155, 42), "Step")
    draw_button(pygame.Rect(372, 625, 155, 42), "Restart")

    status = "AI RUNNING" if game.ai_running else "AI PAUSED"
    if game.won:
        status = "2048 REACHED - YOU WIN!"
    elif game.game_over:
        status = "GAME OVER"

    status_text = INFO_FONT.render(status, True, TEXT_COLOR)
    screen.blit(status_text, (BOARD_X, 580))

    details = SMALL_FONT.render(
        f"Last move: {game.last_move}    Moves: {game.move_count}    Search depth: {game.ai_depth}",
        True,
        TEXT_COLOR
    )
    screen.blit(details, (BOARD_X, 690))

    if game.won or game.game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 185))
        screen.blit(overlay, (0, 0))

        message = "You reached 2048!" if game.won else "No more moves!"
        result = TITLE_FONT.render(message, True, TEXT_COLOR)
        hint = INFO_FONT.render("Press Restart to play again", True, TEXT_COLOR)

        screen.blit(result, result.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55)))


def main():
    game = Game2048()
    running = True
    last_ai_move = 0
    ai_interval = 180

    start_button = pygame.Rect(42, 625, 155, 42)
    step_button = pygame.Rect(207, 625, 155, 42)
    restart_button = pygame.Rect(372, 625, 155, 42)

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_SPACE:
                    game.ai_running = not game.ai_running
                elif event.key == pygame.K_PERIOD:
                    game.ai_step()
                elif event.key in DIRECTION_KEYS and not game.ai_running:
                    game.play(DIRECTION_KEYS[event.key])

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    if not game.game_over and not game.won:
                        game.ai_running = not game.ai_running
                elif step_button.collidepoint(event.pos):
                    game.ai_running = False
                    game.ai_step()
                elif restart_button.collidepoint(event.pos):
                    game.reset()

        if game.ai_running and current_time - last_ai_move >= ai_interval:
            game.ai_step()
            last_ai_move = current_time

        draw_game(game)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

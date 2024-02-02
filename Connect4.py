import numpy as np
import random
import pygame
import sys
import math

# Constants
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1
PLAYER2 = 2

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

# Game state variables
menu = True
game_over = False

pygame.init()

# Game Setup
SQUARE_SIZE = 100
width = COLUMN_COUNT * SQUARE_SIZE
height = (ROW_COUNT + 1) * SQUARE_SIZE
size = (width, height)
RADIUS = int(SQUARE_SIZE / 2 - 5)
screen = pygame.display.set_mode(size)

pygame.font.init()
myfont = pygame.font.SysFont("monospace", 75)


# Function to create the game board
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


# Function to drop a piece onto the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece


# Function to check if a location is valid for placing a piece
def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


# Function to get the next open row in a column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


# Function to print the board
def print_board(board):
    print(np.flip(board, 0))


# Function to check if a player has won
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True


# Function to evaluate a window or scoring
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


# Function to score the position of the board for a given player
def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


# Function to check if the game has reached a terminal state
def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


# Function for the minimax algorithm to find the best move
def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, 100000000000000
            elif winning_move(board, PLAYER_PIECE):
                return None, -10000000000000
            else:  # Game is over, no more valid moves
                return None, 0
        else:  # Depth is zero
            return None, score_position(board, AI_PIECE)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col

            beta = min(beta, value)

            if alpha >= beta:
                break

        return column, value


# Function to get the valid locations for placing a piece
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


# Function to pick the best move
def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col


# Function to draw the game board
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK, (
                int(c * SQUARE_SIZE + SQUARE_SIZE / 2), int(r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (
                    int(c * SQUARE_SIZE + SQUARE_SIZE / 2), height - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (
                    int(c * SQUARE_SIZE + SQUARE_SIZE / 2), height - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
    pygame.display.update()


board = create_board()
print_board(board)

turn = random.randint(PLAYER, AI)


# Function to start a new game
def start_player_vs_player_mode():
    global game_over, board, turn
    global mode
    mode = "Player vs Player"
    board = create_board()
    print_board(board)
    game_over = False
    turn = random.randint(PLAYER, AI)
    draw_board(board)


# Function to start a new player vs computer game
def start_player_vs_computer():
    global game_over, board, turn
    global mode
    mode = "Player vs AI"
    board = create_board()
    print_board(board)
    game_over = False
    turn = random.randint(PLAYER, AI)
    draw_board(board)


# Function to quit the game
def quit_game():
    pygame.quit()
    sys.exit()


# Constants for interface buttons
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_COLOR = (0, 200, 0)
BUTTON_HOVER_COLOR = (0, 255, 0)
QUIT_BUTTON_COLOR = (255, 0, 0)
QUIT_BUTTON_HOVER_COLOR = (255, 0, 0)


# Function to draw buttons on the interface
def draw_button(text, x, y, width, height, default_color, hover_color, action):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1:
            action()
        else:
            pygame.draw.rect(screen, default_color, (x, y, width, height))

        button_font = pygame.font.SysFont('monospace', 15)
        button_text = button_font.render(text, True, BLACK)
        screen.blit(button_text, (x + width // 2 - button_text.get_width() // 2, y + height // 2 - button_text.get_height() // 2))
    else:
        pygame.draw.rect(screen, default_color, (x, y, width, height))
        button_font = pygame.font.SysFont('monospace', 15)
        button_text = button_font.render(text, True, BLACK)
        screen.blit(button_text, (x + width // 2 - button_text.get_width() // 2, y + height // 2 - button_text.get_height() // 2))


# Function to handle the menu
def handle_menu():
    global menu
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)

        # Draw menu options
        draw_button("Player vs Player", width // 2 - BUTTON_WIDTH // 2, height // 2 - 2 * BUTTON_HEIGHT, BUTTON_WIDTH,
                    BUTTON_HEIGHT, BUTTON_COLOR, BUTTON_HOVER_COLOR, start_player_vs_player_mode)
        draw_button("Player vs Computer", width // 2 - BUTTON_WIDTH // 2, height // 2 - BUTTON_HEIGHT, BUTTON_WIDTH,
                    BUTTON_HEIGHT, BUTTON_COLOR, BUTTON_HOVER_COLOR, start_player_vs_computer)
        draw_button("Quit", width // 2 - BUTTON_WIDTH // 2, height // 2, BUTTON_WIDTH, BUTTON_HEIGHT, QUIT_BUTTON_COLOR,
                    QUIT_BUTTON_HOVER_COLOR, quit_game)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False  # Exit the menu loop and close the game

            if event.type == pygame.MOUSEBUTTONDOWN:
                posx, posy = pygame.mouse.get_pos()

                # Check if the mouse click is within the "Player vs Player" button
                if width // 2 - BUTTON_WIDTH // 2 < posx < width // 2 - BUTTON_WIDTH // 2 + BUTTON_WIDTH and \
                        height // 2 - 2 * BUTTON_HEIGHT < posy < height // 2 - 2 * BUTTON_HEIGHT + BUTTON_HEIGHT:
                    start_player_vs_player_mode()  # Start the player vs player game
                    menu = False

                # Check if the mouse click is within the "Player vs Computer" button
                elif width // 2 - BUTTON_WIDTH // 2 < posx < width // 2 - BUTTON_WIDTH // 2 + BUTTON_WIDTH and \
                        height // 2 - BUTTON_HEIGHT < posy < height // 2 - BUTTON_HEIGHT + BUTTON_HEIGHT:
                    start_player_vs_computer()  # Start the player vs computer game
                    menu = False

                # Check if the mouse click is within the "Quit" button
                elif width // 2 - BUTTON_WIDTH // 2 < posx < width // 2 - BUTTON_WIDTH // 2 + BUTTON_WIDTH and \
                        height // 2 < posy < height // 2 + BUTTON_HEIGHT:
                    quit_game()  # Quit the game
                    menu = False


# Pygame initialisation
pygame.init()
pygame.font.init()

handle_menu()

# Main game loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARE_SIZE / 2)), RADIUS)
            elif mode == "Player vs Player":
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARE_SIZE / 2)), RADIUS)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))

            # Ask for Player 1 Input
            if turn == 0:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARE_SIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1)

                    if winning_move(board, 1):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

            # Ask for Player 2 Input in "Player vs Player" mode
            elif mode == "Player vs Player" and turn == 1:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARE_SIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 2)

                    if winning_move(board, 2):
                        label = myfont.render("Player 2 wins!!", 1, YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

            print_board(board)
            draw_board(board)

        # Ask for AI Input in "Player vs AI" mode
        elif mode == "Player vs AI" and turn == 1 and not game_over:
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("Player 2 wins!!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True

                turn += 1
                turn = turn % 2

            print_board(board)
            draw_board(board)

        if game_over:
            pygame.time.wait(3000)

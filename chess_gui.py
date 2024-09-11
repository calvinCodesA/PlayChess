import pygame
import os
from chess import ChessBoard, ChessPiece, Pawn, Rook, Knight, Bishop, Queen, King
import random
import time
from enum import Enum
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 640, 480
BOARD_SIZE = 480
SQUARE_SIZE = BOARD_SIZE // 8
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess (Created by Calvin Sowah)")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
HOVER_COLOR = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Fonts
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)

# Load chess piece images
def load_piece_images():
    pieces = {}
    original_size = int(SQUARE_SIZE * 0.8)  # 80% of the square size
    new_width = int(original_size * 0.7)  # 70% of the original width (30% less wide)
    new_height = original_size  # Keep the original height

    for color in ['white', 'black']:
        folder = 'White' if color == 'white' else 'Black'
        for piece in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
            image_path = os.path.join('ChessPiece', folder, f'{piece}.png')
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(image, (new_width, new_height))
            pieces[f'{color}_{piece}'] = image
    return pieces

PIECE_IMAGES = load_piece_images()

# Load sound effects
MOVE_SOUND = pygame.mixer.Sound('move.mp3')
CAPTURE_SOUND = pygame.mixer.Sound('capture.mp3')

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class ChessGui:
    def __init__(self):
        self.board = ChessBoard()
        self.selected_piece = None
        self.current_player = 'white'  # White (bottom) moves first
        self.game_mode = None
        self.move_history = []
        self.game_state = 'ongoing'
        self.ai = None
        self.ai_move_delay = 1.0  # Delay for AI moves in seconds

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = WHITE if (row + col) % 2 == 0 else GRAY
                pygame.draw.rect(SCREEN, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.board[7-row][col]  # Flip the row
                if piece != ' ':
                    piece_type = type(piece).__name__.lower()
                    image = PIECE_IMAGES[f'{piece.color}_{piece_type}']
                    x = col * SQUARE_SIZE + (SQUARE_SIZE - image.get_width()) // 2
                    y = row * SQUARE_SIZE + (SQUARE_SIZE - image.get_height()) // 2
                    SCREEN.blit(image, (x, y))

    def draw_captured_pieces(self):
        for color in ['white', 'black']:
            y_offset = 0 if color == 'white' else HEIGHT // 2
            for i, piece in enumerate(self.board.captured_pieces[color]):
                piece_type = type(piece).__name__.lower()
                image = PIECE_IMAGES[f'{piece.color}_{piece_type}']
                scaled_width = SQUARE_SIZE // 2 * 0.7  # 30% less wide
                scaled_height = SQUARE_SIZE // 2
                image = pygame.transform.scale(image, (int(scaled_width), int(scaled_height)))
                x = BOARD_SIZE + (i % 4) * (SQUARE_SIZE // 2)
                y = y_offset + (i // 4) * (SQUARE_SIZE // 2)
                SCREEN.blit(image, (x, y))

    def handle_click(self, pos):
        col, row = pos[0] // SQUARE_SIZE, 7 - (pos[1] // SQUARE_SIZE)  # Flip the row
        if self.selected_piece:
            start = self.selected_piece
            end = (col, row)
            
            # Check if it's a castling move
            if isinstance(self.board.board[start[1]][start[0]], King) and abs(start[0] - end[0]) == 2:
                if self.handle_castling(start, end):
                    self.selected_piece = None
                    self.switch_player()
                    return
            
            if self.board.is_valid_move(start, end):
                self.board.move_piece(start, end, check_only=False)
                piece = self.board.board[row][col]
                if isinstance(piece, Pawn):
                    if (piece.color == 'white' and row == 7) or (piece.color == 'black' and row == 0):
                        self.promote_pawn(col, row)
                self.move_history.append((start, end))
                if self.board.board[row][col] != ' ':
                    CAPTURE_SOUND.play()
                else:
                    MOVE_SOUND.play()
                self.switch_player()
            self.selected_piece = None
        else:
            piece = self.board.board[row][col]
            if piece != ' ' and piece.color == self.current_player:
                self.selected_piece = (col, row)

    def switch_player(self):
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.game_state = self.board.get_game_state(self.current_player)
        if self.game_mode == '1 Player' and self.current_player == 'black':
            # Use pygame.time.set_timer to schedule the AI move
            pygame.time.set_timer(pygame.USEREVENT, int(self.ai_move_delay * 1000))

    def ai_move(self):
        if self.ai:
            start, end = self.ai.get_best_move(self.board, self.current_player)
            if start and end:
                if self.board.move_piece(start, end, check_only=False):
                    self.move_history.append((start, end))
                    
                    # Check for pawn promotion
                    piece = self.board.board[end[1]][end[0]]
                    if isinstance(piece, Pawn):
                        if (piece.color == 'white' and end[1] == 7) or (piece.color == 'black' and end[1] == 0):
                            self.board.board[end[1]][end[0]] = Queen(piece.color)
                    
                    if self.board.board[end[1]][end[0]] != ' ':
                        CAPTURE_SOUND.play()
                    else:
                        MOVE_SOUND.play()
                    self.switch_player()

    def handle_castling(self, start, end):
        king = self.board.board[start[1]][start[0]]
        if not isinstance(king, King) or king.has_moved:
            return False

        # Determine if it's kingside or queenside castling
        if end[0] > start[0]:  # Kingside
            rook_start = (7, start[1])
            rook_end = (5, start[1])
            king_end = (6, start[1])
        else:  # Queenside
            rook_start = (0, start[1])
            rook_end = (3, start[1])
            king_end = (2, start[1])

        rook = self.board.board[rook_start[1]][rook_start[0]]
        if not isinstance(rook, Rook) or rook.has_moved:
            return False

        # Check if the path is clear and not under attack
        if not self.board.is_castling_legal(start, king_end):
            return False

        # Perform the castling move
        self.board.board[king_end[1]][king_end[0]] = king
        self.board.board[start[1]][start[0]] = ' '
        self.board.board[rook_end[1]][rook_end[0]] = rook
        self.board.board[rook_start[1]][rook_start[0]] = ' '
        king.has_moved = True
        rook.has_moved = True

        MOVE_SOUND.play()
        return True

    def promote_pawn(self, col, row):
        promotion_pieces = [Queen, Rook, Bishop, Knight]
        piece_color = self.board.board[row][col].color
        
        # Calculate dimensions for promotion options
        original_size = int(SQUARE_SIZE * 0.54)  # 54% of the square size
        option_width = int(original_size * 0.7)  # 70% of the original width (30% less wide)
        option_height = original_size  # Keep the original height
        padding = int(SQUARE_SIZE * 0.1)  # Keep the same padding
        total_width = (option_width + padding) * len(promotion_pieces) - padding
        
        # Calculate starting position (centered above the pawn)
        start_x = col * SQUARE_SIZE + (SQUARE_SIZE - total_width) // 2
        start_y = max(0, (7-row) * SQUARE_SIZE - option_height - padding)  # Ensure it's not off-screen
        
        # Draw promotion options
        for i, piece_class in enumerate(promotion_pieces):
            piece = piece_class(piece_color)
            x = start_x + i * (option_width + padding)
            y = start_y
            
            # Draw background for option
            pygame.draw.rect(SCREEN, WHITE, (x, y, option_width, option_height))
            pygame.draw.rect(SCREEN, BLACK, (x, y, option_width, option_height), 2)  # Keep the border thickness
            
            # Draw piece image
            piece_image = PIECE_IMAGES[f'{piece_color}_{piece_class.__name__.lower()}']
            scaled_image = pygame.transform.scale(piece_image, (option_width, option_height))
            SCREEN.blit(scaled_image, (x, y))
        
        pygame.display.flip()
        
        # Wait for player to choose promotion piece
        waiting_for_promotion = True
        while waiting_for_promotion:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = pygame.mouse.get_pos()
                    if start_y <= click_pos[1] < start_y + option_height:
                        for i in range(len(promotion_pieces)):
                            option_x = start_x + i * (option_width + padding)
                            if option_x <= click_pos[0] < option_x + option_width:
                                new_piece = promotion_pieces[i](piece_color)
                                self.board.board[row][col] = new_piece
                                waiting_for_promotion = False
                                break
        
        # Redraw the board to show the promoted piece
        self.draw_board()
        self.draw_pieces()
        pygame.display.flip()

    def draw_selection_screen(self):
        SCREEN.fill(WHITE)
        title = FONT.render("Select Game Mode", True, BLACK)
        one_player = FONT.render("1 Player", True, BLACK)
        two_player = FONT.render("2 Players", True, BLACK)

        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        pygame.draw.rect(SCREEN, GREEN, (WIDTH // 4, HEIGHT // 2, WIDTH // 2, 50))
        pygame.draw.rect(SCREEN, RED, (WIDTH // 4, HEIGHT * 3 // 4, WIDTH // 2, 50))
        SCREEN.blit(one_player, (WIDTH // 2 - one_player.get_width() // 2, HEIGHT // 2 + 10))
        SCREEN.blit(two_player, (WIDTH // 2 - two_player.get_width() // 2, HEIGHT * 3 // 4 + 10))

    def draw_difficulty_selection(self):
        # Create a gradient background
        background = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            r = int((y / HEIGHT) * (DARK_BLUE[0] - LIGHT_BLUE[0]) + LIGHT_BLUE[0])
            g = int((y / HEIGHT) * (DARK_BLUE[1] - LIGHT_BLUE[1]) + LIGHT_BLUE[1])
            b = int((y / HEIGHT) * (DARK_BLUE[2] - LIGHT_BLUE[2]) + LIGHT_BLUE[2])
            pygame.draw.line(background, (r, g, b), (0, y), (WIDTH, y))
        SCREEN.blit(background, (0, 0))

        title = FONT.render("Select AI Difficulty", True, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 6))

        difficulties = ["Easy", "Medium", "Hard"]
        button_width, button_height = WIDTH // 2, 50
        button_x = WIDTH // 4
        start_y = HEIGHT // 3

        mouse_pos = pygame.mouse.get_pos()

        for i, difficulty in enumerate(difficulties):
            button_y = start_y + i * (button_height + 20)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(mouse_pos):
                color = HOVER_COLOR
            else:
                color = WHITE

            pygame.draw.rect(SCREEN, color, button_rect)
            pygame.draw.rect(SCREEN, BLACK, button_rect, 2)  # Add a black outline
            
            text = FONT.render(difficulty, True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            SCREEN.blit(text, text_rect)

    def draw(self):
        self.draw_board()
        self.draw_pieces()
        self.draw_captured_pieces()

        if self.selected_piece:
            x, y = self.selected_piece
            pygame.draw.rect(SCREEN, LIGHT_BLUE, (x * SQUARE_SIZE, (7-y) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        # Clear the area where the text might have been
        clear_rect = pygame.Rect(BOARD_SIZE + 10, HEIGHT - 60, WIDTH - BOARD_SIZE - 20, 60)
        pygame.draw.rect(SCREEN, WHITE, clear_rect)

        if self.game_state == 'check' or self.game_state in ['checkmate', 'stalemate']:
            if self.game_state == 'check':
                game_state_text = f"{self.current_player.capitalize()} is in check!"
            else:
                game_state_text = f"Game Over: {self.game_state.capitalize()}"
            game_state_surface = SMALL_FONT.render(game_state_text, True, RED)
            text_x = BOARD_SIZE + 10
            text_y = HEIGHT - 50
            SCREEN.blit(game_state_surface, (text_x, text_y))

        pygame.display.flip()

    def run(self):
        running = True
        difficulty_selected = False
        while running:
            if self.game_mode is None:
                self.draw_selection_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        if WIDTH // 4 <= x <= WIDTH * 3 // 4:
                            if HEIGHT // 2 <= y <= HEIGHT // 2 + 50:
                                self.game_mode = '1 Player'
                            elif HEIGHT * 3 // 4 <= y <= HEIGHT * 3 // 4 + 50:
                                self.game_mode = '2 Players'
                                difficulty_selected = True
            elif self.game_mode == '1 Player' and not difficulty_selected:
                self.draw_difficulty_selection()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        button_width, button_height = WIDTH // 2, 50
                        button_x = WIDTH // 4
                        start_y = HEIGHT // 3
                        for i, difficulty in enumerate(["Easy", "Medium", "Hard"]):
                            button_y = start_y + i * (button_height + 20)
                            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                            if button_rect.collidepoint(x, y):
                                difficulty = i + 2  # Easy: 2, Medium: 3, Hard: 4
                                self.ai = ChessAI(difficulty)
                                difficulty_selected = True
                                break
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.game_state != 'checkmate' and self.game_state != 'stalemate':
                            pos = pygame.mouse.get_pos()
                            if pos[0] < BOARD_SIZE:
                                self.handle_click(pos)
                    elif event.type == pygame.USEREVENT:
                        # AI move event
                        pygame.time.set_timer(pygame.USEREVENT, 0)  # Stop the timer
                        self.ai_move()

                self.draw()

            pygame.display.flip()

        pygame.quit()

class MCTSNode:
    def __init__(self, board, move=None, parent=None):
        self.board = board
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.score = 0

class ChessAI:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.max_thinking_time = 5  # Maximum thinking time in seconds
        self.current_board = None
        self.max_depth = 2 if difficulty == Difficulty.MEDIUM else 4 if difficulty == Difficulty.HARD else 1
        self.exploration_constant = 1.41  # UCT exploration constant

    def get_best_move(self, board, color):
        self.current_board = board
        self.current_color = color
        moves = self.get_all_valid_moves(color)
        
        if not moves:
            return None

        if self.difficulty == Difficulty.EASY:
            return random.choice(moves)
        elif self.difficulty == Difficulty.MEDIUM:
            return self.get_best_move_minimax(board, color)
        else:  # HARD
            return self.get_best_move_mcts(board, color)
    
    def get_best_move_minimax(self, board, color):
        best_score = float('-inf') if color == 'white' else float('inf')
        best_move = None
        
        for move in self.get_all_valid_moves(color):
            new_board = ChessBoard()
            new_board.board = [row[:] for row in board.board]
            new_board.move_piece(move[0], move[1], check_only=False)
            score = self.minimax(new_board, self.max_depth - 1, float('-inf'), float('inf'), color == 'black')
            
            if color == 'white':
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
        
        return best_move
    

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.get_game_state('white' if maximizing_player else 'black') != 'ongoing':
            return self.simulate(board, 'white' if maximizing_player else 'black')
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_valid_moves('white'):
                new_board = ChessBoard()
                new_board.board = [row[:] for row in board.board]
                new_board.move_piece(move[0], move[1], check_only=False)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_valid_moves('black'):
                new_board = ChessBoard()
                new_board.board = [row[:] for row in board.board]
                new_board.move_piece(move[0], move[1], check_only=False)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
        
    def get_best_move_mcts(self, board, color):
        root = MCTSNode(board)
        end_time = time.time() + self.max_thinking_time

        while time.time() < end_time:
            leaf = self.select(root)
            child = self.expand(leaf, color)
            result = self.simulate(child.board, color)
            self.backpropagate(child, result)

        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def select(self, node):
        while node.children:
            if not all(child.visits > 0 for child in node.children):
                return self.expand(node, self.current_color)
            node = self.uct_select(node)
        return node

    def expand(self, node, color):
        moves = self.get_all_valid_moves(color)
        for move in moves:
            new_board = ChessBoard()  # Create a new ChessBoard instance
            new_board.board = [row[:] for row in node.board.board]  # Copy the board state
            new_board.move_piece(move[0], move[1], check_only=False)
            child = MCTSNode(new_board, move, node)
            node.children.append(child)
        return random.choice(node.children) if node.children else None

    def simulate(self, board, color):
        temp_board = ChessBoard()  # Create a new ChessBoard instance
        temp_board.board = [row[:] for row in board.board]  # Copy the board state
        current_color = color
        max_moves = 100  # Prevent infinite games

        for _ in range(max_moves):
            if temp_board.get_game_state(current_color) != 'ongoing':
                break
            moves = self.get_all_valid_moves(current_color)
            if not moves:
                break
            move = random.choice(moves)
            temp_board.move_piece(move[0], move[1], check_only=False)
            current_color = 'black' if current_color == 'white' else 'white'

        return self.evaluate_board(temp_board)
    

    def evaluate_board(self, board):
        if board.get_game_state('white') == 'checkmate':
            return -1000  # Black wins
        elif board.get_game_state('black') == 'checkmate':
            return 1000  # White wins
        elif board.get_game_state('white') == 'stalemate' or board.get_game_state('black') == 'stalemate':
            return 0  # Draw

        score = 0
        piece_values = {
            Pawn: 100, Knight: 320, Bishop: 330, Rook: 500, Queen: 900, King: 20000
        }

        # Piece square tables for positional scoring
        piece_position_tables = {
            Pawn: [
                0,  0,  0,  0,  0,  0,  0,  0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5,  5, 10, 25, 25, 10,  5,  5,
                0,  0,  0, 20, 20,  0,  0,  0,
                5, -5,-10,  0,  0,-10, -5,  5,
                5, 10, 10,-20,-20, 10, 10,  5,
                0,  0,  0,  0,  0,  0,  0,  0
            ],
            Knight: [
                -50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50,
            ],
            Bishop: [
                -20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20,
            ],
            Rook: [
                0,  0,  0,  0,  0,  0,  0,  0,
                5, 10, 10, 10, 10, 10, 10,  5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                0,  0,  0,  5,  5,  0,  0,  0
            ],
            Queen: [
                -20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                -5,  0,  5,  5,  5,  5,  0, -5,
                0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20
            ],
            King: [
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -20,-30,-30,-40,-40,-30,-30,-20,
                -10,-20,-20,-20,-20,-20,-20,-10,
                20, 20,  0,  0,  0,  0, 20, 20,
                20, 30, 10,  0,  0, 10, 30, 20
            ]
        }

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece != ' ':
                    piece_type = type(piece)
                    piece_value = piece_values[piece_type]
                    position_value = piece_position_tables[piece_type][row * 8 + col]
                    
                    if piece.color == 'white':
                        score += piece_value + position_value
                    else:
                        score -= piece_value + position_value

        # Evaluate pawn structure
        for col in range(8):
            white_pawns = sum(1 for row in range(8) if isinstance(board.board[row][col], Pawn) and board.board[row][col].color == 'white')
            black_pawns = sum(1 for row in range(8) if isinstance(board.board[row][col], Pawn) and board.board[row][col].color == 'black')
            
            if white_pawns > 1:
                score -= 10 * (white_pawns - 1)  # Penalize doubled pawns
            if black_pawns > 1:
                score += 10 * (black_pawns - 1)  # Penalize doubled pawns

        # Evaluate control of the center
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        for row, col in center_squares:
            piece = board.board[row][col]
            if piece != ' ':
                if piece.color == 'white':
                    score += 10
                else:
                    score -= 10

        # Evaluate king safety
        white_king_pos = next((i, j) for i, row in enumerate(board.board) for j, piece in enumerate(row) if isinstance(piece, King) and piece.color == 'white')
        black_king_pos = next((i, j) for i, row in enumerate(board.board) for j, piece in enumerate(row) if isinstance(piece, King) and piece.color == 'black')

        # Penalize if kings are not in their starting positions (assuming they haven't castled)
        if white_king_pos != (0, 4):
            score -= 20
        if black_king_pos != (7, 4):
            score += 20

        # Evaluate piece development (encourage pieces to move from their starting positions)
        if isinstance(board.board[0][1], Knight):
            score -= 10
        if isinstance(board.board[0][6], Knight):
            score -= 10
        if isinstance(board.board[7][1], Knight):
            score += 10
        if isinstance(board.board[7][6], Knight):
            score += 10

        if isinstance(board.board[0][2], Bishop):
            score -= 10
        if isinstance(board.board[0][5], Bishop):
            score -= 10
        if isinstance(board.board[7][2], Bishop):
            score += 10
        if isinstance(board.board[7][5], Bishop):
            score += 10

        return score

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if result is not None:  # Add this check
                node.score += result
            node = node.parent

    def uct_select(self, node):
        return max(node.children, key=lambda c: c.score / c.visits + 
                   self.exploration_constant * math.sqrt(math.log(node.visits) / c.visits))

    def get_all_valid_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.current_board.board[row][col]
                if piece != ' ' and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.current_board.is_valid_move((col, row), (end_col, end_row)):
                                moves.append(((col, row), (end_col, end_row)))
        return moves

if __name__ == "__main__":
    chess_gui = ChessGui()
    chess_gui.run()

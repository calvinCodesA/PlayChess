import asyncio

class ChessPiece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False

    def is_valid_move(self, board, start, end):
        if not isinstance(start, tuple) or not isinstance(end, tuple):
            return False
        if len(start) != 2 or len(end) != 2:
            return False
        
        x1, y1 = start
        x2, y2 = end
        
        if end is None:
            return False
        if isinstance(board.board[y2][x2], ChessPiece) and board.board[y2][x2].color == self.color:
            return False
        return True

    def __str__(self):
        return f"{self.color} {self.__class__.__name__}"

class Pawn(ChessPiece):
    def is_valid_move(self, board, start, end):
        if not super().is_valid_move(board, start, end):
            return False
        x1, y1 = start
        x2, y2 = end
        if self.color == 'white':
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # Normal move
        if x1 == x2 and y2 == y1 + direction and board.board[y2][x2] == ' ':
            return True
        
        # First move - two squares
        if x1 == x2 and y2 == y1 + 2 * direction and y1 == start_row and board.board[y1 + direction][x1] == ' ' and board.board[y2][x2] == ' ':
            return True
        
        # Capture
        if abs(x2 - x1) == 1 and y2 == y1 + direction and isinstance(board.board[y2][x2], ChessPiece) and board.board[y2][x2].color != self.color:
            return True
        
        # En passant
        if abs(x2 - x1) == 1 and y2 == y1 + direction and board.board[y2][x2] == ' ':
            if board.last_move:
                last_start_x, last_start_y, last_end_x, last_end_y = board.last_move
                if (last_end_x == x2 and last_end_y == y1 and
                    isinstance(board.board[y1][x2], Pawn) and
                    board.board[y1][x2].color != self.color and
                    abs(last_start_y - last_end_y) == 2):
                    return True

        return False

class Rook(ChessPiece):
    def is_valid_move(self, board, start, end):
        if not super().is_valid_move(board, start, end):
            return False
        x1, y1 = start
        x2, y2 = end
        if x1 != x2 and y1 != y2:
            return False
        step_x = 0 if x1 == x2 else (1 if x2 > x1 else -1)
        step_y = 0 if y1 == y2 else (1 if y2 > y1 else -1)
        x, y = x1 + step_x, y1 + step_y
        while (x, y) != (x2, y2):
            if board.board[y][x] != ' ':
                return False
            x, y = x + step_x, y + step_y
        return True

class Knight(ChessPiece):
    def is_valid_move(self, board, start, end):
        if not super().is_valid_move(board, start, end):
            return False
        x1, y1 = start
        x2, y2 = end
        return (abs(x2 - x1) == 2 and abs(y2 - y1) == 1) or (abs(x2 - x1) == 1 and abs(y2 - y1) == 2)

class Bishop(ChessPiece):
    def is_valid_move(self, board, start, end):
        if not super().is_valid_move(board, start, end):
            return False
        x1, y1 = start
        x2, y2 = end
        if abs(x2 - x1) != abs(y2 - y1):
            return False
        step_x = 1 if x2 > x1 else -1
        step_y = 1 if y2 > y1 else -1
        x, y = x1 + step_x, y1 + step_y
        while (x, y) != (x2, y2):
            if board.board[y][x] != ' ':
                return False
            x, y = x + step_x, y + step_y
        return True

class Queen(ChessPiece):
    def is_valid_move(self, board, start, end):
        if not super().is_valid_move(board, start, end):
            return False
        
        x1, y1 = start
        x2, y2 = end
        
        # Check if the move is along a rank, file, or diagonal
        if x1 == x2 or y1 == y2 or abs(x2 - x1) == abs(y2 - y1):
            # Determine the direction of movement
            dx = 0 if x2 == x1 else (1 if x2 > x1 else -1)
            dy = 0 if y2 == y1 else (1 if y2 > y1 else -1)
            
            # Check if the path is clear
            x, y = x1 + dx, y1 + dy
            while (x, y) != (x2, y2):
                if board.board[y][x] != ' ':
                    return False
                x, y = x + dx, y + dy
            
            return True
        
        return False

class King(ChessPiece):
    def is_valid_move(self, board, start, end):
        if not isinstance(start, tuple) or not isinstance(end, tuple) or len(start) != 2 or len(end) != 2:
            return False

        x1, y1 = start
        x2, y2 = end

        # Normal king move
        if abs(x2 - x1) <= 1 and abs(y2 - y1) <= 1:
            return super().is_valid_move(board, start, end)

        # Castling
        if y1 == y2 and abs(x2 - x1) == 2:
            if self.has_moved:
                return False

            # Kingside castling
            if x2 > x1:
                rook_x = 7
                empty_squares = [(x1 + 1, y1), (x1 + 2, y1)]
            # Queenside castling
            else:
                rook_x = 0
                empty_squares = [(x1 - 1, y1), (x1 - 2, y1), (x1 - 3, y1)]

            rook = board.board[y1][rook_x]
            if not isinstance(rook, Rook) or rook.has_moved:
                return False

            # Check if squares between king and rook are empty
            if not all(board.board[y][x] == ' ' for x, y in empty_squares):
                return False

            # Check if king is not in check and doesn't pass through check
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if board.is_square_under_attack((x, y1), self.color):
                    return False

            return True

        return False

class ChessBoard:
    def __init__(self):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
        self.move_history = []
        self.last_move = None
        self.captured_pieces = {'white': [], 'black': []}
        self.check_task = None
        self.is_in_check = {'white': False, 'black': False}

    def setup_pieces(self):
        for i in range(8):
            self.board[1][i] = Pawn('white')
            self.board[6][i] = Pawn('black')
        
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, piece_class in enumerate(piece_order):
            self.board[0][i] = piece_class('white')
            self.board[7][i] = piece_class('black')

    async def check_king_status(self):
        while True:
            self.is_in_check['white'] = self.is_king_in_check('white')
            self.is_in_check['black'] = self.is_king_in_check('black')
            await asyncio.sleep(0.5)  # Check every 0.5 seconds

    def start_check_task(self):
        if self.check_task is None or self.check_task.done():
            self.check_task = asyncio.create_task(self.check_king_status())

    def stop_check_task(self):
        if self.check_task:
            self.check_task.cancel()

    def move_piece(self, start, end, check_only=False):
        x1, y1 = start
        x2, y2 = end
        piece = self.board[y1][x1]
        
        if not isinstance(piece, ChessPiece):
            return False

        if not piece.is_valid_move(self, start, end):
            return False

        # Make the move temporarily
        temp_piece = self.board[y2][x2]
        self.board[y2][x2] = piece
        self.board[y1][x1] = ' '

        # Handle en passant capture
        en_passant_capture = None
        if isinstance(piece, Pawn) and abs(x2 - x1) == 1 and temp_piece == ' ':
            if piece.color == 'white' and y1 == 4:
                en_passant_capture = self.board[y1][x2]
                self.board[y1][x2] = ' '
            elif piece.color == 'black' and y1 == 3:
                en_passant_capture = self.board[y1][x2]
                self.board[y1][x2] = ' '

        # Check if the move leaves the king in check
        king_in_check = self.is_king_in_check(piece.color)

        if king_in_check:
            # Undo the move
            self.board[y1][x1] = piece
            self.board[y2][x2] = temp_piece
            if en_passant_capture:
                self.board[y1][x2] = en_passant_capture
            return False

        if check_only:
            # Undo the move and return
            self.board[y1][x1] = piece
            self.board[y2][x2] = temp_piece
            if en_passant_capture:
                self.board[y1][x2] = en_passant_capture
            return True

        # The move is valid, proceed with the actual move
        if isinstance(temp_piece, ChessPiece):
            self.captured_pieces[temp_piece.color].append(temp_piece)
        elif en_passant_capture:
            self.captured_pieces[en_passant_capture.color].append(en_passant_capture)

        # Update last move
        self.last_move = (x1, y1, x2, y2)

        # After a successful move, update the check status
        self.is_in_check['white'] = self.is_king_in_check('white')
        self.is_in_check['black'] = self.is_king_in_check('black')

        return True

    def is_valid_move(self, start, end, check_king_safety=True):
        piece = self.board[start[1]][start[0]]
        if not isinstance(piece, ChessPiece):
            return False

        if not piece.is_valid_move(self, start, end):
            return False

        # Temporarily make the move
        temp_piece = self.board[end[1]][end[0]]
        self.board[end[1]][end[0]] = self.board[start[1]][start[0]]
        self.board[start[1]][start[0]] = ' '

        # Check if the move puts or leaves the king in check
        valid = True
        if check_king_safety:
            if self.is_king_in_check(piece.color):
                valid = False

        # Undo the temporary move
        self.board[start[1]][start[0]] = self.board[end[1]][end[0]]
        self.board[end[1]][end[0]] = temp_piece

        return valid

    def promote_pawn(self, color):
        # In a real game, you'd ask the player what piece they want to promote to
        # For simplicity, we'll always promote to a Queen
        return Queen(color)

    def undo_move(self):
        if self.move_history:
            start, end, captured_piece = self.move_history.pop()
            moved_piece = self.board[end[1]][end[0]]
            self.board[start[1]][start[0]] = moved_piece
            self.board[end[1]][end[0]] = captured_piece
            if isinstance(moved_piece, ChessPiece):
                moved_piece.has_moved = False
            if isinstance(captured_piece, ChessPiece):
                if captured_piece in self.captured_pieces[captured_piece.color]:
                    self.captured_pieces[captured_piece.color].remove(captured_piece)
            self.last_move = None

    def is_king_in_check(self, color):
        # Find the king's position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (col, row)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # King not found (shouldn't happen in a valid game)

        # Check if any opponent's piece can attack the king
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != ' ' and piece.color == opponent_color:
                    if self.is_valid_move((col, row), king_pos, check_king_safety=False):
                        return True

        return False

    def is_square_under_attack(self, square, color):
        if not isinstance(square, tuple) or len(square) != 2:
            return False
        
        opponent_color = 'black' if color == 'white' else 'white'
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, ChessPiece) and piece.color == opponent_color:
                    try:
                        if piece.is_valid_move(self, (x, y), square):
                            return True
                    except Exception:
                        pass
        return False

    def find_king(self, color):
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, King) and piece.color == color:
                    return (x, y)
        return None

    def is_checkmate(self, color):
        if not self.is_king_in_check(color):
            return False
        
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, ChessPiece) and piece.color == color:
                    for end_y in range(8):
                        for end_x in range(8):
                            if self.move_piece((x, y), (end_x, end_y), check_only=True):
                                return False
        return True

    def is_stalemate(self, color):
        if self.is_king_in_check(color):
            return False
        
        # Check if any legal move is available
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, ChessPiece) and piece.color == color:
                    for end_y in range(8):
                        for end_x in range(8):
                            if self.move_piece((x, y), (end_x, end_x), check_only=True):
                                return False
        return True

    def get_game_state(self, current_player):
        if self.is_checkmate(current_player):
            return 'checkmate'
        if self.is_stalemate(current_player):
            return 'stalemate'
        if self.is_in_check[current_player]:
            return 'check'
        return 'ongoing'

    def display(self):
        for row in self.board:
            print(' '.join(str(piece)[0] if piece != ' ' else '.' for piece in row))

        # Display captured pieces
        print("\nCaptured pieces:")
        print("White:", ', '.join(str(piece) for piece in self.captured_pieces['white']))
        print("Black:", ', '.join(str(piece) for piece in self.captured_pieces['black']))

    def is_valid_move_out_of_check(self, color, start, end):
        x1, y1 = start
        x2, y2 = end
        piece = self.board[y1][x1]
        if not isinstance(piece, ChessPiece) or piece.color != color:
            return False
        
        if not piece.is_valid_move(self, start, end):
            return False
        
        # Make the move temporarily
        temp_piece = self.board[y2][x2]
        self.board[y2][x2] = piece
        self.board[y1][x1] = ' '
        
        # Check if the move takes the king out of check
        king_out_of_check = not self.is_king_in_check(color)
        
        # Undo the move
        self.board[y1][x1] = piece
        self.board[y2][x2] = temp_piece
        
        return king_out_of_check

    def print_board(self):
        for y in range(7, -1, -1):
            row = []
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, ChessPiece):
                    row.append(f"{piece.color[0]}{type(piece).__name__[0]}")
                else:
                    row.append(".")
            print(" ".join(row))
        print()

    def print_valid_moves_in_check(self, color):
        valid_moves = []
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if isinstance(piece, ChessPiece) and piece.color == color:
                    for end_y in range(8):
                        for end_x in range(8):
                            if piece.is_valid_move(self, (x, y), (end_x, end_y)):
                                # Temporarily make the move
                                temp_piece = self.board[end_y][end_x]
                                self.board[end_y][end_x] = piece
                                self.board[y][x] = ' '
                                
                                # Check if the king is still in check
                                if not self.is_king_in_check(color):
                                    valid_moves.append(((x, y), (end_x, end_y)))
                                
                                # Undo the move
                                self.board[y][x] = piece
                                self.board[end_y][end_x] = temp_piece

        print(f"Valid moves for {color} when king is in check:")
        for start, end in valid_moves:
            piece = self.board[start[1]][start[0]]
            print(f"{type(piece).__name__} from {start} to {end}")

    def is_castling_legal(self, start, end):
        x1, y1 = start
        x2, y2 = end
        
        # Check if the squares between the king and rook are empty
        step = 1 if x2 > x1 else -1
        for x in range(x1 + step, 7 if step > 0 else 0, step):
            if self.board[y1][x] != ' ':
                return False

        # Check if the king is not in check and doesn't pass through check
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.is_square_under_attack((x, y1), self.board[y1][x1].color):
                return False

        return True

async def play_chess():
    board = ChessBoard()
    board.start_check_task()
    current_player = 'white'
    try:
        while True:
            board.display()
            start = input("Enter start position (e.g., e2): ")
            end = input("Enter end position (e.g., e4): ")
            start = (ord(start[0]) - ord('a'), int(start[1]) - 1)
            end = (ord(end[0]) - ord('a'), int(end[1]) - 1)
            if board.move_piece(start, end):
                current_player = 'black' if current_player == 'white' else 'white'
            await asyncio.sleep(0.1)  # Small delay to allow other tasks to run
    finally:
        board.stop_check_task()

if __name__ == "__main__":
    asyncio.run(play_chess())

# Chess

A fully-functional chess game implemented in Python using Pygame. This game features a graphical user interface, AI opponent, and supports all standard chess rules including en passant, castling, and pawn promotion.

## Features

- Graphical user interface using Pygame
- Single-player mode against AI opponent
- Two-player mode for local multiplayer
- Full implementation of chess rules:
  - En passant
  - Castling (both kingside and queenside)
  - Pawn promotion
- Move validation
- Check and checkmate detection
- Stalemate detection
- Move history
- Captured pieces display
- Sound effects for moves and captures

## Installation

1. Ensure you have Python 3.7+ installed on your system.
2. Install Pygame:
   ```
   pip install pygame
   ```
3. Clone this repository:
   ```
   git clone https://github.com/yourusername/Chess.git
   ```
4. Navigate to the project directory:
   ```
   cd Chess
   ```

## Usage

Run the game by executing:

python3 chess_gui.py

https://github.com/user-attachments/assets/0bfcd29e-8886-4f09-b6f2-9eda997cfc56



## Gameplay

1. **Starting the Game**: Upon launching, you'll be presented with a mode selection screen. Choose between "1 Player" (vs AI) or "2 Players" (local multiplayer).

2. **Making Moves**: Click on a piece to select it, then click on a valid destination square to move. Invalid moves will be ignored.

3. **Special Moves**:
   - **Castling**: Move the king two squares towards a rook to castle.
   - **En Passant**: Move a pawn diagonally to capture an opponent's pawn that just moved two squares.
   - **Pawn Promotion**: When a pawn reaches the opposite end of the board, click on the desired piece to promote to.

4. **Game End**: The game ends upon checkmate or stalemate. A message will be displayed indicating the result.

## Gameplay Examples

### Castling
Kingside Castling:



https://github.com/user-attachments/assets/cc0efcfb-f8a0-4285-9030-4a372fbcce43



### En Passant

https://github.com/user-attachments/assets/37724750-2d5f-496e-a38a-509c0deb1da4


### Pawn Promotion

https://github.com/user-attachments/assets/198cbde7-ca47-497a-af70-b5da6b324962



## AI Opponent

The game features an AI opponent with multiple difficulty levels. The AI uses a minimax algorithm with alpha-beta pruning, which is a common approach in game theory and artificial intelligence for making optimal decisions in two-player games.

### Difficulty Levels

1. **Easy** : The AI plays random valid moves. This level is suitable for beginners or casual players.
2. **Medium** (Depth 3): The AI looks ahead 3 moves using the minimax algorithm.
3. **Hard** (Depth 4): The AI uses Monte Carlo Simulation to find optimal moves.

### How the AI Works

The AI uses the following components to make decisions:

1. **Minimax Algorithm**: This is a recursive algorithm that simulates all possible moves up to a certain depth. It assumes that the opponent will always make the best possible move.

2. **Alpha-Beta Pruning**: This is an optimization technique that significantly reduces the number of nodes evaluated by the minimax algorithm. It stops evaluating a move when it's determined that the move is worse than a previously examined move.

3. **Evaluation Function**: This function assigns a score to each board position. It considers factors such as:
   - Material balance (value of pieces)
   - Piece positions (e.g., controlling the center is good)
   - King safety
   - Pawn structure

4. **Move Ordering**: The AI tries to evaluate the most promising moves first to improve the efficiency of alpha-beta pruning.

### AI Decision Making Process

1. When it's the AI's turn, it generates all possible moves.
2. For each move, it simulates making that move on an internal copy of the board.
3. It then recursively simulates the opponent's best responses and its own best counter-responses up to the specified depth.
4. At the maximum depth, it uses the evaluation function to assign a score to the position.
5. These scores are propagated back up the game tree, with the AI choosing the move that leads to the best worst-case scenario.

### Limitations and Future Improvements

- The AI doesn't use an opening book, so its play in the opening phase might not follow established theory.
- Endgame play could be improved with specialized evaluation functions for common endgame scenarios.
- The search depth is fixed, but more advanced chess engines use dynamic depth based on the position's complexity.
- Time management is basic; the AI uses a fixed thinking time regardless of the game phase or position complexity.

Future improvements could include implementing an opening book, improving endgame play, using iterative deepening, and implementing more sophisticated time management.

### Performance Considerations

The AI's thinking time increases significantly with each increase in depth. On average:
- Easy (Depth 2): < 1 second per move
- Medium (Depth 3): 1-5 seconds per move
- Hard (Depth 4): 5-20 seconds per move

These times can vary based on the complexity of the position and the performance of the hardware running the game.
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgments

- Chess piece images from (https://www.rawpixel.com/image/6285730/png-sticker-public-domain)
- Sound effects from (https://www.chess.com/forum/view/general/chessboard-sound-files)




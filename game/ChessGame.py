from utils.sizes import *
from utils.globalParameters import *
from utils.board import *
from time import time

en_passant_target = None

def initialize_game_timer(game_time_minutes):
    # Initialize the game timer for a chess match.
    
    total_time_seconds = game_time_minutes * 60
    return {"white": total_time_seconds, "black": total_time_seconds}


def update_and_display_timer(screen, font, timers, turn, start_time):
    current_time = time()
    elapsed_time = current_time - start_time
    window_width, window_height = screen.get_size()

    # Update the timer for the current player
    timers[turn] -= elapsed_time
    start_time = current_time

    # Ensure timers don't go below zero
    timers["white"] = max(0, timers["white"])
    timers["black"] = max(0, timers["black"])

    # Create the text for the timers
    white_timer = font.render(f"White: {int(timers['white'] // 60)}:{int(timers['white'] % 60):02} s", True, (0, 0, 0))
    black_timer = font.render(f"Black: {int(timers['black'] // 60)}:{int(timers['black'] % 60):02} s", True, (0, 0, 0))


    # Clear the areas where the timers are displayed (using the same background color)
    pygame.draw.rect(screen, WHITE, (window_width - 200, 160, 115, 50))  # Clear white timer area
    pygame.draw.rect(screen, WHITE, (window_width - 200, 190, 115, 50))  # Clear black timer area

    # Display the updated timers in the new positions
    screen.blit(white_timer, (window_width - 200, 160))  # White timer position
    screen.blit(black_timer, (window_width - 200, 190))  # Black timer position


    return start_time


def check_en_passant(initial_pieces, move_history, turn):
    global en_passant_target
    en_passant_target = None  # Reset the target

    if not move_history:
        return []
    
    # Extract the last move details
    last_move = move_history[-1]
    last_turn, start_pos, end_pos = last_move
    start_row, start_col = from_algebraic(start_pos)
    end_row, end_col = from_algebraic(end_pos)

    # Check if the last move was a double pawn push
    if abs(start_row - end_row) == 2:  # Double push
        if initial_pieces[end_row][end_col] == f"P_{last_turn}":  # Opponent's pawn
            # The row where the en passant capture would occur
            capture_row = end_row - (1 if turn == "white" else -1)
            possible_captures = []

            # Check adjacent columns for current turn's pawn
            for dc in [-1, 1]:  # Left and right neighbors
                adj_col = end_col + dc
                if 0 <= adj_col < BOARD_SIZE:  # Ensure within board bounds
                    if initial_pieces[end_row][adj_col] == f"P_{turn}":
                        # Add en passant move for the adjacent pawn
                        possible_captures.append(((end_row, adj_col), (capture_row, end_col)))
            return possible_captures

    return []



def get_moves(board, row, col, piece, turn):
    """
    Generates all valid moves for a piece, including en passant.
    """
    # Check and print en_passant_target for debugging
    #print(f"Before: en_passant_target = {en_passant_target}")
    global en_passant_target
    moves = []
    opponent = "white" if turn == "black" else "black"
    piece_type = piece.split("_")[0]

    directions = {
        "P": [(-1, 0), (-1, -1), (-1, 1)] if turn == "white" else [(1, 0), (1, -1), (1, 1)],
    }

    def is_valid_move(r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and (not board[r][c] or opponent in board[r][c])

    if piece_type == "P":
        # Pawn moves
        for dr, dc in directions["P"]:
            nr, nc = row + dr, col + dc
            if dc == 0:  # Move forward
                if is_valid_move(nr, nc) and not board[nr][nc]:
                    moves.append((nr, nc))
                    if (row == 1 and turn == "black") or (row == 6 and turn == "white"):
                        nr2 = nr + dr
                        if is_valid_move(nr2, nc) and not board[nr2][nc]:
                            moves.append((nr2, nc))
            else:  # Capture diagonally
                if is_valid_move(nr, nc) and opponent in (board[nr][nc] or ""):
                    moves.append((nr, nc))
        # Add en passant moves for this specific pawn
        en_passant_moves = check_en_passant(board, moves_history, turn)
        for (start_pos, target_pos) in en_passant_moves:
            if (row, col) == start_pos:
                moves.append(target_pos)
                en_passant_target=target_pos

    return moves 


def is_winner(board, turn):
    # Check for pawn reaching the last row
    def has_pawn_reached_last_row(board, color):
        if color == 'white':
            # Check if any white pawns are on row 0
            for col in range(8):
                if board[0][col] == 'P_white':
                    return True
        elif color == 'black':
            # Check if any black pawns are on row 7
            for col in range(8):
                if board[7][col] == 'P_black':
                    return True
        return False

    # Check for opponent having no pawns
    def has_opponent_no_pawns(board, color):
        opponent_color = 'white' if color == 'black' else 'black'
        for row in range(8):
            for col in range(8):
                if (color == 'white' and board[row][col] == 'P_black') or (color == 'black' and board[row][col] == 'P_white'):
                    return False
        return True

    # Check if the opponent has no valid moves left
    def opponent_has_no_moves(board, color):
        opponent_color = 'white' if color == 'black' else 'black'
        
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if (color == 'white' and 'white' in piece) or (color == 'black' and 'black' in piece):
                    # Check for valid moves for this piece
                    moves = get_moves(board, row, col, piece, color)
                    if moves:
                        return False  # The player can still move
        return True  # The opponent has no moves left

    # Check if the game is won by the current player
    if has_pawn_reached_last_row(board, turn):
        return turn  # Return winner color: 'white' or 'black'
    
    if has_opponent_no_pawns(board, turn):
        return turn  # Return winner color: 'white' or 'black'
    
    if opponent_has_no_moves(board, turn):
        opponent_color = 'black' if turn == 'white' else 'white'
        return opponent_color  # Return the opponent (loser's) color

    return None  # No winner yet

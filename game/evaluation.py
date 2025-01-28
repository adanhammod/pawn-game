from game.ChessGame import *
from utils.sizes import BOARD_SIZE

# Constants for scoring
PIECE_VALUES = {"P": 1}
BONUS_ADVANCED_ROW = 20
BONUS_PROXIMITY_PROMOTION = 100
BONUS_SECOND_LAST_ROW = 50
BONUS_PROTECTING_PAWN = 10
BONUS_THREATENING_ENEMY = 30
BONUS_ISOLATED_PAWN= 20


PENALTY_DOUBLED_PAWN = -1
PENALTY_ISOLATED_PAWN = -2
PENALTY_PAWN_DANGER = -50
PENALTY_PAWN_BLOCKED = -30

def evaluate_state(state, turn):
    material_score = 0
    pawn_structure_score = 0
    danger_score = 0

    # Precompute legal moves for both sides
    legal_moves_white = get_all_legal_moves(state, "white")
    legal_moves_black = get_all_legal_moves(state, "black")

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = state[row][col]

            if piece:
                material_score += get_piece_value(piece)
                pawn_structure_score += evaluate_pawn_structure(state, row, col, piece)

                if piece.startswith("P"):
                    if is_opponent_trapped(state, turn, legal_moves_white, legal_moves_black):
                        danger_score += 5

    mobility_score = get_pawn_mobility(state, legal_moves_white, legal_moves_black)

    # Combine scores
    total_score = (
        material_score + pawn_structure_score + mobility_score + danger_score
    )
    return total_score


def is_opponent_trapped(state, turn, legal_moves_white, legal_moves_black):
    """Check if the opponent has no legal moves (checkmate or stalemate)."""
    opponent_turn = "black" if turn == "white" else "white"
    legal_moves = legal_moves_black if opponent_turn == "black" else legal_moves_white
    return len(legal_moves) == 0


def get_piece_value(piece):
    """Get the material value of a piece."""
    if not piece:
        return 0
    type_, color = piece.split("_")
    value = PIECE_VALUES.get(type_, 0)
    return value


def get_pawn_mobility(state, legal_moves_white, legal_moves_black):
    """Evaluate pawn mobility, promotion potential, and advanced row bonuses."""
    mobility_score = 0

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = state[row][col]
            if piece and piece.startswith("P"):  # if it's a pawn
                color = piece.split("_")[1]
                legal_moves = legal_moves_white if color == "white" else legal_moves_black

                # Mobility based on the number of legal moves
                mobility_score += len(legal_moves)

                # Bonus for being in advanced rows
                if color == "white":
                    mobility_score += BONUS_ADVANCED_ROW if row == 3 else 0
                elif color == "black":
                    mobility_score += BONUS_ADVANCED_ROW if row == 4 else 0

                # Bonus for proximity to promotion
                if (color == "white" and row == 1) or (color == "black" and row == 6):
                    mobility_score += BONUS_PROXIMITY_PROMOTION

                # Bonus for second-last rank
                elif (color == "white" and row == 2) or (color == "black" and row == 5):
                    mobility_score += BONUS_SECOND_LAST_ROW

                # Bonus for defending other pawns
                if is_defending_other_pawn(state, row, col, color):
                    mobility_score += BONUS_PROTECTING_PAWN

                # Bonus for threatening an enemy piece
                if can_threaten_enemy_piece(state, row, col, color):
                    mobility_score += BONUS_THREATENING_ENEMY

    return mobility_score


def is_defending_other_pawn(state, row, col, color):
    """Checks if the pawn is protecting another pawn."""
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down
    for drow, dcol in directions:
        new_row, new_col = row + drow, col + dcol
        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            adjacent_piece = state[new_row][new_col]
            if adjacent_piece and adjacent_piece.startswith("P") and adjacent_piece.split("_")[1] == color:
                return True
    return False


def can_threaten_enemy_piece(state, row, col, color):
    """Checks if the pawn is threatening an opponent's piece."""
    directions = [(-1, -1), (-1, 1)] if color == "white" else [(1, -1), (1, 1)]
    for drow, dcol in directions:
        new_row, new_col = row + drow, col + dcol
        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            enemy_piece = state[new_row][new_col]
            if enemy_piece and not enemy_piece.startswith("P_" + color):
                return True
    return False


def evaluate_pawn_structure(state, row, col, piece):
    _, color = piece.split("_")
    direction = -1 if color == "white" else 1
    pawn_structure_score = 0

    # Check for doubled pawns
    if 0 <= row + direction < BOARD_SIZE:
        same_column_piece = state[row + direction][col]
        if same_column_piece and same_column_piece.startswith("P_" + color):
            #print(f"Pawn at ({row},{col}) is doubled with pawn at ({row + direction},{col})")
            pawn_structure_score += PENALTY_DOUBLED_PAWN

    # Check for isolated pawns
    has_support = any(
        0 <= col + dcol < BOARD_SIZE
        and 0 <= row + direction < BOARD_SIZE
        and state[row + direction][col + dcol] == f"P_{color}"
        for dcol in [-1, 1]
    )
    in_danger= check_pawn_situation(state, row, col, piece, "danger")
    if not has_support and not in_danger:
        pawn_structure_score+= BONUS_ISOLATED_PAWN
    else:    
        pawn_structure_score += PENALTY_ISOLATED_PAWN

    can_capture = check_pawn_situation(state, row, col, piece, "capture")
    if can_capture:
        pawn_structure_score+=30

    # Danger, blocked, and capture situations
    if in_danger:
        #print(f"Pawn at ({row},{col}) is in danger")
        pawn_structure_score += PENALTY_PAWN_DANGER

    if check_pawn_situation(state, row, col, piece, "blocked"):
        #print(f"Pawn at ({row},{col}) is blocked ,{color}")
        pawn_structure_score += PENALTY_PAWN_BLOCKED

    return pawn_structure_score


def check_pawn_situation(state, row, col, piece, situation_type):
    """Check specific situations for a pawn like danger or being blocked."""
    _, color = piece.split("_")
    opponent_color = "black" if color == "white" else "white"
    direction = -1 if color == "white" else 1

    if situation_type == "danger":
        # Check if the pawn is threatened by an enemy piece
        threat_directions = [(-direction, -1), (-direction, 1)]
        for drow, dcol in threat_directions:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                enemy_piece = state[new_row][new_col]
                if enemy_piece and enemy_piece.startswith(f"P_{opponent_color}"):
                    return True

    elif situation_type == "blocked":
        # Check if the pawn is blocked by another piece
        forward_row = row + direction
        if 0 <= forward_row < BOARD_SIZE:
            if state[forward_row][col] != "":
                #print(f"hi {row}, {col}")
                return True
            

    elif situation_type == "capture":
        # Check if the pawn can capture an enemy piece
        capture_directions = [(-direction, -1), (-direction, 1)]  # Diagonal directions
        for drow, dcol in capture_directions:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                enemy_piece = state[new_row][new_col]
                if enemy_piece and enemy_piece.startswith(f"P_{opponent_color}"):
                    return True  # Pawn can capture the enemy piece        
    return False


def get_all_legal_moves(board, turn):
    """Return all legal moves for the current board and turn."""
    legal_moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and turn in piece:
                moves = get_moves(board, row, col, piece, turn)
                for move in moves:
                    legal_moves.append(((row, col), move))
                
    return legal_moves
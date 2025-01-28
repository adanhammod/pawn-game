last_move=None
screen = None 
highlighted_squares = []
moves_history = [] # Global variable to store move history
last_move = None
game_time_minutes=10

board = [
    ["", "", "", "", "", "", "", ""],  
    ["P_black", "P_black", "P_black", "P_black", "P_black", "P_black", "P_black", "P_black"],  # Black pawns
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],  
    ["", "", "", "", "", "", "", ""], 
    ["", "", "", "", "", "", "", ""],
    ["P_white", "P_white", "P_white", "P_white", "P_white", "P_white", "P_white", "P_white"],  # White pawns
    ["", "", "", "", "", "", "", ""], 
]

def get_moves_history():
    # Retrieves the current moves history.
    return moves_history

def update_moves_history(move):
    # Updates the moves history with a new move.
    global moves_history
    assert isinstance(move, tuple), "Move must be a tuple"
    assert len(move) == 3, "Move must have 3 elements: turn, start_square, end_square"
    
    moves_history.append(move)



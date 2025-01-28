from game.evaluation import *
import time

class ChessAI:
    def __init__(self, ai_color="black", depth=4, total_time=120):
        """
        Initialize the AI with its color, depth, and time constraints.
        """
        self.ai_color = ai_color  # "white" or "black"
        self.depth = depth  # Depth of the Minimax search
        self.total_time = total_time  # Total time for the AI (in seconds)
        self.start_time = None  # Start time for the game
        self.remaining_time = total_time  # Remaining time for the AI

    def start_timer(self):
        """
        Start or reset the timer for a move.
        """
        self.start_time = time.time()

    def has_time_remaining(self):
        """
        Check if there is still time remaining for the AI.
        """
        elapsed = time.time() - self.start_time
        return self.remaining_time - elapsed > 0

    def update_remaining_time(self):
        """
        Update the remaining time based on the last move duration.
        """
        elapsed = time.time() - self.start_time
        self.remaining_time -= elapsed
        self.start_time = None

    def minimax(self, state, depth, is_maximizing_player, turn, alpha=float("-inf"), beta=float("inf")):
        """
        Minimax algorithm with Alpha-Beta pruning.
        """
        if depth == 0 or is_game_end(state) or not self.has_time_remaining():
            return evaluate_state(state, turn)

        legal_moves = get_all_legal_moves(state, turn)

        if is_maximizing_player:
            best_value = float("-inf")
            for move in legal_moves:
                prev_piece = self.apply_move(state, move, turn)
                move_value = self.minimax(state, depth - 1, False, "white" if turn == "black" else "black", alpha, beta)
                self.undo_move(state, move, prev_piece)


                best_value = max(best_value, move_value)
                alpha = max(alpha, best_value)
                if beta <= alpha or not self.has_time_remaining():
                    break
            return best_value
        else:
            best_value = float("inf")
            for move in legal_moves:
                prev_piece = self.apply_move(state, move, turn)
                move_value = self.minimax(state, depth - 1, True, "white" if turn == "black" else "black", alpha, beta)
                self.undo_move(state, move, prev_piece)


                best_value = min(best_value, move_value)
                beta = min(beta, best_value)
                if beta <= alpha or not self.has_time_remaining():
                    break
            return best_value

    def find_best_move(self, state):
  
        self.start_timer()
        best_move = None
        best_value = float("-inf") if self.ai_color == "white" else float("inf")

        legal_moves = get_all_legal_moves(state, self.ai_color)

        for move in legal_moves:
            if not self.has_time_remaining():
                print("no time")
                break
            
            prev_piece = self.apply_move(state, move, self.ai_color)
            move_value = self.minimax(state, self.depth - 1, self.ai_color == "black", "white" if self.ai_color == "black" else "black")
            #print(f"Evaluating Move: {move}, Value: {move_value}")
            self.undo_move(state, move, prev_piece)

            # Debug: Print the current best_value and the move being evaluated
            #print(f"Move: {move}, Evaluated Value: {move_value}")

            # Check if the move value should update the best move
            if self.ai_color == "white":
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move

       
        self.update_remaining_time()
        return best_move

    def apply_move(self, state, move, turn):
        """
        Apply the move to the board and save the previous state of the destination cell.
        """
        start, end = move
        prev_piece = state[end[0]][end[1]]  # Save the previous piece in the destination cell
        state[end[0]][end[1]] = state[start[0]][start[1]]
        state[start[0]][start[1]] = ""  # Clear the original cell
        return prev_piece

    def undo_move(self, state, move, prev_piece):
        """
        Undo the move and restore the previous board state.
        """
        start, end = move
        state[start[0]][start[1]] = state[end[0]][end[1]]  # Move the piece back to the original cell
        state[end[0]][end[1]] = prev_piece  # Restore the previous content of the destination cell


def ai_move(board, turn, time):
    """
    Interface to use the MinimaxAI for selecting the next move.
    """
    agent = ChessAI(ai_color=turn, depth=4, total_time=time)  # Adjust total_time as needed (e.g., 10 seconds)
    agent.start_timer()  # Start the timer for the game/move
    # print("Current Board State:")
    # for row in board:
    #     print(" ".join([cell if cell else "." for cell in row]))  # Print '.' for empty cells

    legal_moves = get_all_legal_moves(board, turn)
    if not legal_moves:
        return None  # No moves possible, game over

    best_move = agent.find_best_move(board)
    #print(f"Best Move {best_move}")
    return best_move


def is_game_end(state):
    """
    Check if the game is in EndGame.
    """
    if is_winner(state, "white") or is_winner(state, "black"):
        return True
    return False

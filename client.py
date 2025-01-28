import pygame
import socket
import threading
from utils.board import *
from utils.colors import *
from utils.globalParameters import *
from main import *

# Create a socket instance
socketObject = socket.socket()

# Connect to the server (localhost, port 9999)
socketObject.connect(("localhost", 9999))
offset_x = (WINDOW_WIDTH - CHESSBOARD_SIZE) // 2
offset_y = (WINDOW_HEIGHT - CHESSBOARD_SIZE) // 2
piece_images = load_piece_images()
global color, running
global color_turn, round
game_started = False  # Flag to indicate when to display the screen
running = True


def display_timer(screen,  white_time, black_time):
    """Display the current timer for each player in MM:SS format."""
    font = pygame.font.SysFont("Comic Sans MS", 20)

    # Convert time to minutes and seconds
    white_minutes = int(white_time) // 60
    white_seconds = int(white_time) % 60
    black_minutes = int(black_time) // 60
    black_seconds = int(black_time) % 60

    # Format the time as MM:SS
    white_time_text = font.render(f"White: {white_minutes:02}:{white_seconds:02}", True, (0, 0, 0))
    black_time_text = font.render(f"Black: {black_minutes:02}:{black_seconds:02}", True, (0, 0, 0))
    
    # Display the times on the screen
    screen.blit(white_time_text, (20, 20))  # Display white's time
    screen.blit(black_time_text, (WINDOW_WIDTH - black_time_text.get_width() - 20, 20))  # Display black's time

def update_timer():
    """Update the timer based on the current turn."""
    global white_time_remaining, black_time_remaining, last_time_update, color

    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - last_time_update) / 1000  # Convert to seconds

    if color_turn == "white":
        white_time_remaining -= elapsed_time
    elif color_turn == "black":
        black_time_remaining -= elapsed_time

    last_time_update = current_time  # Update the last time when the timer was updated

    # Prevent timer from going below 0
    white_time_remaining = max(0, white_time_remaining)
    black_time_remaining = max(0, black_time_remaining)



def redraw_board(screen, offset_x, offset_y, piece_images, board):
    """ Redraw the chessboard and pieces on the screen after a move or update. """
    draw_chessboard(screen, offset_x, offset_y)  # Redraw the chessboard
    draw_pieces(screen, piece_images, offset_x, offset_y, board)  # Redraw the pieces
    pygame.display.update()  # Update the display

def handle_ai(turn,  remaining_time):
    """ Handle the AI's turn. """
    global board, moves_history, piece_images, color_turn

    move = ai_move(board, turn, int(remaining_time/14))
    if move:
        (start_row, start_col), (end_row, end_col) = move
        update_moves_history((turn, to_algebraic(start_row, start_col), to_algebraic(end_row, end_col)))

        # Move the piece
        handle_move(start_row, start_col, end_row, end_col)

        # Handle special cases like en passant or castling if necessary
        en_passant_targets = check_en_passant(board, moves_history, turn)
        if en_passant_targets and (end_row, end_col) == en_passant_targets[0][1]:
            board[end_row][end_col] = board[start_row][start_col]
            board[start_row][start_col] = ""  # Clear starting position
            board[en_passant_targets[0][1][0]][en_passant_targets[0][1][1]] = ""
        return True
    return False

def parse_setup(setup_command):
    """Parse the Setup command and create the board."""
    setup_pieces = setup_command.split()[1:]  # Skip the "Setup" word
    board = [["" for _ in range(8)] for _ in range(8)]  # Create an 8x8 empty board

    for piece in setup_pieces:
        color = "P_white" if piece[0] == "W" else "P_black"
        column = ord(piece[1]) - ord('a')  # Convert column letter to index (0-based)
        row = 8 - int(piece[2])  # Convert row number to index (0-based, reversed)
        board[row][column] = color  # Place the piece on the board
    return board

def handle_move(start_row, start_col, end_row, end_col):
    """Update the board after a move."""
    board[end_row][end_col] = board[start_row][start_col]
    board[start_row][start_col] = ""  # Clear starting position

def from_algebraic(square):
    """ Convert algebraic notation (e.g., 'e2') to board indices. """
    col = ord(square[0]) - ord('a')  # 'a' -> 0, 'b' -> 1, etc.
    row = 8 - int(square[1])  # '8' -> 0, '7' -> 1, etc.
    return row, col

def handle_socket_communication(socketObject):
    """ Handle socket communication in a separate thread. """
    global color, board, game_started, color_turn, time, running, time_per_turn_minutes, time_per_turn_seconds, white_time_remaining
    global black_time_remaining, last_time_update
    while running:
        data = socketObject.recv(1024).decode()
        print(f"Server: {data}")

        if data.startswith("Time"):
            time = int(data[5:])
            time_per_turn_minutes = time /2
            time_per_turn_seconds = time_per_turn_minutes * 60  # Convert to seconds
            white_time_remaining = time_per_turn_seconds
            black_time_remaining = time_per_turn_seconds
            last_time_update = pygame.time.get_ticks()
            msg = "OK".encode()
            socketObject.send(msg)

        elif data.startswith("Setup"):
            msg = "OK".encode()
            socketObject.send(msg)
            board = parse_setup(data)
        

        elif data in ["White", "Black"]:
            color = data.lower()
            color_turn = data.lower()
            msg = "OK".encode()
            socketObject.send(msg)

        elif data == "exit":
            print("Connection closed")
            running = False  # Stop the game loop gracefully
            break

        elif data == "Your turn":
            color_turn = color
            winner = is_winner(board, color_turn)
            if winner:
                display_winner(winner)
                msg = f"Win {winner.capitalize()}".encode() 
                socketObject.send(msg)
            else:
                # Pass the remaining time for the current turn
                remaining_time = white_time_remaining if color == "white" else black_time_remaining
                handle_ai(color, remaining_time)
                if screen is not None and running:
                    redraw_board(screen, offset_x, offset_y, piece_images, board)
                ai_last_move = get_moves_history()[-1]
                if ai_last_move:
                    start_square, end_square = ai_last_move[1], ai_last_move[2]
                    msg = f"{start_square}{end_square}"
                    msg = msg.encode()
                    socketObject.send(msg)

        elif data == "Begin":
            msg = "OK".encode()
            socketObject.send(msg)
            game_started = True  # Set the flag to start the game

        elif data in ["White's turn", "Black's turn"]:
            # Send acknowledgment message
            msg = "OK".encode()
            socketObject.send(msg)
            # Update the display to show the current player's turn
            color_turn = "white" if data == "White's turn" else "black"
            if screen is not None:
                display_turn(screen, color_turn)

        elif data == "Connected to the server":
            msg = "OK".encode()
            socketObject.send(msg)

        elif len(data) == 4 and running:  # Opponent move (e.g., 'e2e4')
            start_square, end_square = data[:2], data[2:]
            start_row, start_col = from_algebraic(start_square)
            end_row, end_col = from_algebraic(end_square)
            handle_move(start_row, start_col, end_row, end_col)
            redraw_board(screen, offset_x, offset_y, piece_images, board)

    socketObject.close()  # Ensure the socket is closed when communication ends

# Start socket communication in a separate thread
socket_thread = threading.Thread(target=handle_socket_communication, args=(socketObject,))
socket_thread.start()

# Wait for the game to start
while not game_started:
    pass

# Initialize the game window
pygame.init()
screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
screen.fill(WHITE)
pygame.display.set_caption("Pawn Game")
draw_chessboard(screen, offset_x, offset_y)
draw_pieces(screen, piece_images, offset_x, offset_y, board)
draw_labels(screen, offset_x, offset_y)
display_timer(screen, white_time_remaining, black_time_remaining)  # Display the timer

# Pygame event loop
while running:
    update_timer()  # Update the timer at the beginning of each loop iteration
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if socketObject.fileno() != -1:  # Check if the socket is open
                socketObject.send("exit".encode())
            running = False

    display_turn(screen, color_turn)  
    display_timer(screen, white_time_remaining, black_time_remaining)  # Display the timer


    pygame.display.flip()

pygame.quit()

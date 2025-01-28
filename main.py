import pygame
from game.ChessGame import *  
from utils.board import *  
from tkinter import *
from PIL import Image, ImageTk
from game.minimax import *
from utils.colors import *
from utils.sizes import *
from utils.cover import *
from utils.globalParameters import *
import time

turn = "white"  # Assuming the game starts with white's turn
def display_winner(winner_name):
    # Create a new Tkinter window for the winner message
    root = Tk()
    root.title("Winner!")  # Set the title of the window
    root.geometry("400x300")  # Width x Height in pixels
    root.configure(bg="white")  # Set the background color

    # Load and display the image
    try:
        # Use resource_path to get the correct path for the image
        img_path = resource_path("images/trophy.png")
        img = Image.open(img_path)
        img = img.resize((130, 130), Image.Resampling.LANCZOS)  # Resize the image with high-quality resampling
        tk_img = ImageTk.PhotoImage(img)
    except FileNotFoundError:
        print("Error: The image file was not found. Ensure the path is correct.")
        tk_img = None

    # Add a label for the winner message
    label = Label(root, text=f"The game is over!\n\n {winner_name.capitalize()} wins", font=("Verdana", 12), fg="black", bg="white")
    label.pack(pady=10)

    # Display the image if it was successfully loaded
    if tk_img:
        image_label = Label(root, image=tk_img, bg="white")
        image_label.pack(pady=15)

    # Add a button to close the window
    close_button = Button(root, text="OK", command=root.destroy , width=7, height=1, bg="white")
    close_button.pack(pady=10)

    # Run the Tkinter main loop
    root.mainloop()

def handle_ai_turn(time ):
    global board, moves_history, turn,  timers
    move = ai_move(board, turn,time)
    if move:
        start, end = move
        start_row, start_col = start
        end_row, end_col = end

        # Check for en passant
        en_passant_targets = check_en_passant(board, moves_history, turn)
        if en_passant_targets:
            en_passant_target = en_passant_targets[0][1]  # First target position
         
            if (end_row, end_col) == en_passant_target:
                last_move = moves_history[-1]
                _, _, last_end_pos = last_move
                last_end_row, last_end_col = from_algebraic(last_end_pos)

                # Remove captured pawn
                board[last_end_row][last_end_col] = ""

                # Move capturing pawn
                board[end_row][end_col] = board[start_row][start_col]
                board[start_row][start_col] = ""  # Clear starting position
            else:
            # Handle regular move
             board[end_row][end_col] = board[start_row][start_col]
             board[start_row][start_col] = ""  # Clear starting position
        else:
            # Handle regular move
             board[end_row][end_col] = board[start_row][start_col]
             board[start_row][start_col] = ""  # Clear starting position     

        # Update move history
        moves_history.append((turn, to_algebraic(start_row, start_col), to_algebraic(end_row, end_col)))



def reset_game():
    global board, highlighted_squares, moves_history, selected_square, turn
    board = reset_board()
    moves_history.clear()
    highlighted_squares = []
    selected_square = None
    turn = "white"

def initialize():
    global screen, highlighted_squares, board, turn, en_passant_target
    pygame.init()
    
    # Set up the screen and its properties
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Pawn Game")

    # Load piece images and set up timers
    piece_images = load_piece_images()
    timers = initialize_game_timer(game_time_minutes)
    start_time = time.time()  # Initialize the start time
    font = pygame.font.SysFont("Georgia", 16)

    # Initialize game state
    highlighted_squares = []
    turn = "white"  # Starting with white's turn
    en_passant_target = None  # En passant initially is None

    # UI elements for the game
    start_button_rect = None
    title_text = pygame.font.SysFont("Comic Sans MS", 35, bold=True).render("Pawn Chess", True, BLACK)
    title_rect = title_text.get_rect()
    title_rect.center = (500, 50)  # Center the title text
    
    clock = pygame.time.Clock()
    
    return piece_images, timers, start_time, font, title_text, title_rect, start_button_rect, clock

def reset_game_state():
    global timers, start_time
    reset_game()
    timers = initialize_game_timer(game_time_minutes)
    start_time = time.time()
    font = pygame.font.SysFont("Georgia", 16)
    update_and_display_timer(screen, font, timers, turn, start_time)
    
    

def handle_en_passant(start_row, start_col, row, col):
    en_passant_target = check_en_passant(board, moves_history, turn)
    if en_passant_target and len(en_passant_target) > 0:
        en_passant_target = en_passant_target[0][1]  # Use the target position from the first capture
    if en_passant_target == (row, col):
        last_move = moves_history[-1]
        _, _, end_pos = last_move
        end_row, end_col = from_algebraic(end_pos)
        board[end_row][end_col] = ""  # Remove captured pawn
        board[row][col] = board[start_row][start_col]  # Move capturing pawn
        board[start_row][start_col] = ""  # Clear starting position
    else:
        board[row][col] = board[start_row][start_col]
        board[start_row][start_col] = ""  # Clear starting position
    return en_passant_target

def process_turn(selected_square, row, col):
    global highlighted_squares, turn
    start_row, start_col = selected_square
    piece = board[start_row][start_col]
    
    if (turn == "white" and "white" in piece) or (turn == "black" and "black" in piece):
        highlighted_squares = get_moves(board, start_row, start_col, piece, turn)
        
        if (row, col) in highlighted_squares:
            en_passant_target = handle_en_passant(start_row, start_col, row, col)
            last_move = (turn, to_algebraic(start_row, start_col), to_algebraic(row, col))
            moves_history.append(last_move)

            # Check for winner after valid move
            winner = is_winner(board, turn)
            if winner:
                display_winner(winner)
                reset_game_state()
                return highlighted_squares, False  # Do not proceed with turn change if there's a winner

            # If no winner, proceed with turn change
            turn = "black" if turn == "white" else "white"
            return en_passant_target, True
    
    return highlighted_squares, False


def main():
    global screen, highlighted_squares, board, turn, en_passant_target,timers,start_time
    piece_images, timers, start_time, font, title_text, title_rect, start_button_rect, clock = initialize()

    running = True
    selected_square = None
    show_cover = True
    window_width, window_height = screen.get_size()
    offset_x = (window_width - CHESSBOARD_SIZE) // 2
    offset_y = (window_height - CHESSBOARD_SIZE) // 2

    while running:
        for event in pygame.event.get():
            winner = is_winner(board, turn)
            if winner:
                display_winner(winner)
                reset_game_state()

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if handle_reset_button(mouse_pos):
                    reset_game_state()
                if handle_back_button(mouse_pos):
                    show_cover = True
                    screen.blit(cover_image, (0, 0))
                    screen.blit(title_text, title_rect)
                    start_button_rect = draw_start_button(screen)
                    reset_game_state()

                if show_cover:
                    start_button_rect = draw_start_button(screen)
                    if start_button_rect.collidepoint(event.pos):
                        show_cover = False

                mouse_x, mouse_y = event.pos
                col = (mouse_x - offset_x) // SQUARE_SIZE
                row = (mouse_y - offset_y) // SQUARE_SIZE

                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    if selected_square:
                        en_passant_target, valid_move = process_turn(selected_square, row, col)       
                        if valid_move:
                            turn = "black"
                            selected_square = None
                            highlighted_squares = []
                        else:
                            selected_square = None
                            highlighted_squares = []
                    else:
                        piece = board[row][col]
                        if piece and ((turn == "white" and "white" in piece) or (turn == "black" and "black" in piece)):
                            selected_square = (row, col)
                            highlighted_squares = get_moves(board, row, col, piece, turn)

        # Game display updates
        if not show_cover:
            display_turn(screen, turn)
            pygame.display.update()

            # Timer Updates
            current_time = time.time()
            elapsed_time = current_time - start_time
            timers[turn] -= elapsed_time
            start_time = current_time

            # Ensure timers don't go below zero
            timers["white"] = max(0, timers["white"])
            timers["black"] = max(0, timers["black"])

            # End game if timer runs out
            if timers["white"] <= 0 or timers["black"] <= 0:
                display_winner("black" if timers["white"] <= 0 else "white")
                reset_game_state()

        if turn == "black":
            ai_start_time = time.time()
            handle_ai_turn(timers["black"]/18)
            ai_elapsed_time = time.time() - ai_start_time
            timers["black"] -= ai_elapsed_time
            timers["black"] = max(0, timers["black"])
            start_time = time.time()
            # Check for winner after valid move
            winner = is_winner(board, turn)
            if winner:
                display_winner(winner)
                reset_game_state()
                return highlighted_squares, False  # Do not proceed with turn change if there's a winner

            turn = "white"

        screen.fill(WHITE)
        if show_cover:
            screen.blit(cover_image, (0, 0))
            screen.blit(title_text, title_rect)
            start_button_rect = draw_start_button(screen)
        else:
            draw_chessboard(screen, offset_x, offset_y)
            draw_highlighted_squares(screen, offset_x, offset_y, highlighted_squares)
            draw_pieces(screen, piece_images, offset_x, offset_y, board)
            draw_labels(screen, offset_x, offset_y)
            display_turn(screen, turn)
            draw_reset_button(screen)
            draw_back_button(screen)
            update_and_display_timer(screen, font ,timers, turn, start_time)
            load_and_display_timer_icon(screen)

        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()

 
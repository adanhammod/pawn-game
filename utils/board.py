import pygame
import os
from utils.colors import *
from utils.sizes import *
from utils.globalParameters import *

import os
import sys
import pygame

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    # PyInstaller creates a temp folder and stores files in _MEIPASS
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def load_piece_images():
    piece_images = {}
    piece_files = {
        "K_white": "white-king.png",
        "Q_white": "white-queen.png",
        "R_white": "white-rook.png",
        "B_white": "white-bishop.png",
        "N_white": "white-knight.png",
        "P_white": "white-pawn.png",
        "K_black": "black-king.png",
        "Q_black": "black-queen.png",
        "R_black": "black-rook.png",
        "B_black": "black-bishop.png",
        "N_black": "black-knight.png",
        "P_black": "black-pawn.png",
    }

    for piece, file_name in piece_files.items():
        image_path = resource_path(os.path.join("images", file_name))
        piece_images[piece] = pygame.image.load(image_path)

    return piece_images

def load_and_display_timer_icon(screen):
    try:
        screen_width = screen.get_width()
        # Clear the area where the turn message is displayed (top 60 pixels)
        pygame.draw.rect(screen, WHITE, (screen_width - 180, 100, 50, 50))  # Adjust the 60 for your message box height
        
        # Load and resize the timer icon
        timer_icon_path = resource_path("images/stopwatch.png")
        timer_icon = pygame.image.load(timer_icon_path)
        timer_icon = pygame.transform.scale(timer_icon, (45, 45))  # Resize to 50x50
        
        position = (screen_width - 180, 100)  # 10px margin from the top and right edges
        
        # Display the icon on the screen
        screen.blit(timer_icon, position)

    except FileNotFoundError:
        print("Error: Timer icon image not found.")


def display_moves_history(screen, moves_history):
    font = pygame.font.SysFont("Georgia", 15)
    
    # Define the table area (example coordinates)
    table_x, table_y, table_width, table_height = 10, 70, 250, 300  # Adjust width for two columns
    
    # Define the column spacing (decrease for less space)
    column_spacing = 20  # Adjust this value to control the gap between columns
    
    # Clear only the table area
    pygame.draw.rect(screen, WHITE, (table_x, table_y, table_width, table_height))
    
    # Draw table headers
    white_header = font.render("White", True, (0, 0, 0))
    black_header = font.render("Black", True, (0, 0, 0))
    screen.blit(white_header, (table_x + 10, table_y))
    screen.blit(black_header, (table_x + table_width // 2 - column_spacing, table_y))
    
    # Render each move in two columns
    for i, (white_move, black_move) in enumerate(zip(moves_history[::2], moves_history[1::2])):
        # White's move
        white_text = font.render(f"{white_move[1]} -> {white_move[2]}", True, (0, 0, 0))
        screen.blit(white_text, (table_x + 10, table_y + 20 + i * 20))
        
        # Black's move
        black_text = font.render(f"{black_move[1]} -> {black_move[2]}", True, (0, 0, 0))
        screen.blit(black_text, (table_x + table_width // 2 - column_spacing, table_y + 20 + i * 20))

    # Handle the case where White has played an extra move (odd total moves)
    if len(moves_history) % 2 != 0:
        extra_white_move = moves_history[-1]
        extra_white_text = font.render(f"{extra_white_move[1]} -> {extra_white_move[2]}", True, (0, 0, 0))
        screen.blit(extra_white_text, (table_x + 10, table_y + 20 + len(moves_history) // 2 * 20))


# Function to draw chessboard
def draw_chessboard(screen, offset_x, offset_y):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color =  WHITE if (row + col) % 2 == 0 else DARK_BLUE
            pygame.draw.rect(
                screen,
                color,
                (
                    offset_x + col * SQUARE_SIZE,
                    offset_y + row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )


# Function to draw the pieces on the board
def draw_pieces(screen, piece_images, offset_x, offset_y, initial_pieces):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = initial_pieces[row][col]
            if piece:
                piece_image = piece_images.get(piece)
                if piece_image:
                    piece_image = pygame.transform.scale(piece_image, (SQUARE_SIZE, SQUARE_SIZE))
                    screen.blit(
                        piece_image,
                        (offset_x + col * SQUARE_SIZE, offset_y + row * SQUARE_SIZE),
                    )


def display_turn(screen, current_turn):
    font = pygame.font.SysFont("Comic Sans MS", 30)
    text = font.render(f"{current_turn.capitalize()}'s Turn", True, (0, 0, 0))  # Render turn text
    
    # Clear the area where the turn message is displayed
    pygame.draw.rect(screen, WHITE, (0, 0, WINDOW_WIDTH, 60))  # Clear top area (change 60 to your message box height)

    # Render the new turn message at the top center
    screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 10))

def reset_board():
   initial_pieces = [
    ["", "", "", "", "", "", "", ""],  
    ["P_black", "P_black", "P_black", "P_black", "P_black", "P_black", "P_black", "P_black"],  # Black pawns 
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],  
    ["", "", "", "", "", "", "", ""], 
    ["", "", "", "", "", "", "", ""], 
    ["P_white", "P_white", "P_white", "P_white", "P_white", "P_white", "P_white", "P_white"],  # White pawns 
    ["", "", "", "", "", "", "", ""], 
]
   
   return initial_pieces

def draw_back_button(screen):
    button_width = 60
    button_height = 60
    
    # Position the button at the bottom-right corner with a 20px margin
    button_x = WINDOW_WIDTH - button_width - 20  # 20px from the right edge of the screen
    button_y = WINDOW_HEIGHT - button_height - 100  # 20px from the bottom edge of the screen

    # Draw the button (optional background color for the button)
    pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height))

    # Load an image for the button
    try:
        # Use resource_path to get the correct path for the image
        button_image_path = resource_path("images/back.png")
        button_image = pygame.image.load(button_image_path)  
        button_image = pygame.transform.scale(button_image, (60, 60))  # Resize the image to fit within the button
        screen.blit(button_image, (button_x + (button_width - button_image.get_width()) // 2, button_y + (button_height - button_image.get_height()) // 2))  # Blit image on the button
    except pygame.error:
        print("Error: Could not load the image. Ensure the path is correct.")

def handle_back_button(mouse_pos):
    button_width = 60
    button_height = 60

    button_x = WINDOW_WIDTH - button_width - 20
    button_y = WINDOW_HEIGHT - button_height - 100

    if button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
        return True
    return False


def draw_reset_button(screen):
    button_width = 60
    button_height = 60
    
    # Position the button at the bottom-right corner with a 20px margin
    button_x = WINDOW_WIDTH - button_width - 20  # 20px from the right edge of the screen
    button_y = WINDOW_HEIGHT - button_height - 20  # 20px from the bottom edge of the screen

    # Draw the button (optional background color for the button)
    pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height))

    # Load an image for the button
    try:
        # Use resource_path to get the correct path for the image
        button_image_path = resource_path("images/reset.png")
        button_image = pygame.image.load(button_image_path)  
        button_image = pygame.transform.scale(button_image, (60, 60))  # Resize the image to fit within the button
        screen.blit(button_image, (button_x + (button_width - button_image.get_width()) // 2, button_y + (button_height - button_image.get_height()) // 2))  # Blit image on the button
    except pygame.error:
        print("Error: Could not load the image. Ensure the path is correct.")
        
def handle_reset_button(mouse_pos):
    button_width = 200
    button_height = 50

    # Position the button at the bottom-right corner with a 20px margin
    button_x = WINDOW_WIDTH - button_width - 20  # 20px from the right edge of the screen
    button_y = WINDOW_HEIGHT - button_height - 20  # 20px from the bottom edge of the screen

    # Check if the mouse click is inside the button
    if button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
        return True  # Indicate that the button was clicked
    return False


def to_algebraic(row, col):
    """Convert board coordinates to algebraic notation."""
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # File corresponds to columns
    ranks = ['8', '7', '6', '5', '4', '3', '2', '1']  # Rank corresponds to rows
    return files[col] + ranks[row]


def from_algebraic(position):
    """
    Converts a chess algebraic notation (e.g., 'e2') to board indices (row, col).
    position: A string representing the position in algebraic notation.
    Returns: A tuple (row, col) representing the position on the board.
    """
    if len(position) != 2:
        raise ValueError("Invalid algebraic notation")

    col = ord(position[0].lower()) - ord('a')  # Convert column from letter to 0-based index
    row = BOARD_SIZE - int(position[1])       # Convert row from 1-based to 0-based index

    if not (0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE):
        raise ValueError("Position out of board bounds")

    return row, col


# Function to draw highlighted squares
def draw_highlighted_squares(screen ,offset_x, offset_y, highlighted_squares):
    if highlighted_squares is None:
        return
    for row, col in highlighted_squares:
        pygame.draw.rect(
            screen,
            HIGHLIGHT_COLOR,  # Purple color for highlight
            (
                offset_x + col * SQUARE_SIZE,
                offset_y + row * SQUARE_SIZE,
                SQUARE_SIZE,
                SQUARE_SIZE,
            ),
            5  # Set the border width (thickness)
        )

# Function to draw labels for rows and columns
def draw_labels(screen, offset_x, offset_y):
    font = pygame.font.SysFont("Arial", 20)

    # Draw row numbers (1–8) on the left of the chessboard
    for row in range(BOARD_SIZE):
        label = font.render(str(BOARD_SIZE - row), True, BLACK)
        screen.blit(label, (offset_x - 20, offset_y + row * SQUARE_SIZE + SQUARE_SIZE // 3))

    # Draw column letters (a–h) below the chessboard
    for col in range(BOARD_SIZE):
        label = font.render(chr(97 + col), True, BLACK)  # 97 is the ASCII code for 'a'
        screen.blit(label, (offset_x + col * SQUARE_SIZE + SQUARE_SIZE // 3, offset_y + CHESSBOARD_SIZE + 5))
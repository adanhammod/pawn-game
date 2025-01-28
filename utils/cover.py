#The "cover.py" file loads and displays a cover image, adds a credit text, and renders a start button on the screen.

import pygame
import os
from utils.colors import *
from utils.sizes import *
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    # PyInstaller creates a temp folder and stores files in _MEIPASS
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def load_cover_image():
    try:
        # Use resource_path to resolve the correct path
        cover_image_path = resource_path(os.path.join("images", "cover.jpg"))
        cover_image = pygame.image.load(cover_image_path)
        cover_image = pygame.transform.scale(cover_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        return cover_image
    except Exception as e:
        raise
cover_image = load_cover_image()

# Function to draw "Designed by Freepik" credit
def draw_freepik_credit(screen):
    font = pygame.font.SysFont("Georgia", 16)

    text = font.render("Designed by Freepik", True, BLACK)
    text_rect = text.get_rect()
    text_rect.bottomright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10)  # Position at the bottom-right corner
    screen.blit(text, text_rect)

def draw_start_button(screen, button_width=60, button_height=60, alpha=255):
    # Load the button's image
    try:
        # Use resource_path to get the correct path for the image
        button_image_path = resource_path("images/play.png")
        button_image = pygame.image.load(button_image_path)  
        button_image = pygame.transform.scale(button_image, (button_width, button_height))  # Resize the image to the desired dimensions
        button_image.set_alpha(alpha)  # Set transparency if needed
    except pygame.error:
        print("Error: Could not load the button image. Ensure the path is correct.")
        return None  # Exit if the image can't be loaded

    # Button position (centered at the bottom of the screen)
    button_x = WINDOW_WIDTH // 2 - button_width // 2
    button_y = WINDOW_HEIGHT - button_height - 10  # Positioned 10px from the bottom
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Draw any additional elements you need (like credits)
    draw_freepik_credit(screen)

    # Blit the button image
    screen.blit(button_image, (button_x, button_y))

    return button_rect


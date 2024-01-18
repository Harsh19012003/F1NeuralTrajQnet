import pygame
import math

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Set game title
pygame.display.set_caption("Simple Car Game")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# Car dimensions
car_width = 50
car_height = 30

# Car coordinates
car_x = screen_width // 2 - car_width // 2
car_y = screen_height - car_height

# Car speed sensetivity
car_speed_sensetivity = 0.5

# Angle of rotation for the car
car_angle = 0

# Car angle sensetivity
car_angle_sensetivity = 0.3

# Friction
friction = 1

# Function to rotate the car image
def rotate_car(image, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image

# Load car image
car_image = pygame.image.load("car.jpeg")  # Replace with your car image path
car_image = pygame. transform. scale(car_image, (50,30))

# Main game loop
running = True
while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for pressed keys and update car movement
    pressed_keys = pygame.key.get_pressed()

    if not pressed_keys[pygame.K_UP] and not pressed_keys[pygame.K_DOWN]:
        car_speed_sensetivity *= friction  # Apply friction before movement calculations


    if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_DOWN]:
        if pressed_keys[pygame.K_LEFT]:
            car_angle += car_angle_sensetivity * 1.2
        if pressed_keys[pygame.K_RIGHT]:
            car_angle -= car_angle_sensetivity * 1.2
    if pressed_keys[pygame.K_UP]:
        car_x += car_speed_sensetivity * math.cos(math.radians(car_angle))
        car_y -= car_speed_sensetivity * math.sin(math.radians(car_angle))
    if pressed_keys[pygame.K_DOWN]:
        car_x -= car_speed_sensetivity * math.cos(math.radians(car_angle))
        car_y += car_speed_sensetivity * math.sin(math.radians(car_angle))
    # Clear screen
    screen.fill(white)

    # Draw car
    rotated_car_image = rotate_car(car_image, car_angle)
    car_rect = rotated_car_image.get_rect(center=(car_x, car_y))
    screen.blit(rotated_car_image, car_rect)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

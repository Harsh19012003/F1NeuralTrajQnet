import pygame
import math
import pygame.sprite
import ast

pygame.font.init()
font = pygame.font.SysFont('Arial', 12)

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Set game title
pygame.display.set_caption("2D Car Game")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
gray = (150, 150, 150)
yellow = (255, 255, 0)

# pygame fps tracker clock
clock = pygame.time.Clock()
target_fps = 60  # Target FPS - even if we don't hit this, the game will behave the same

# Car dimensions
car_width = 50
car_height = 30

# Car coordinates
car_x = screen_width // 2 - car_width // 2
car_y = screen_height - car_height

# Car physics parameters (independent of FPS)
car_speed = 0  # Current speed
car_angle = 0 # Angle of rotation for the car
car_acceleration = 300  # Units per second²
car_max_speed = 500  # Maximum speed in units per second
car_steering_speed = 180  # Degrees per second
car_friction = 1.5  # Friction coefficient (applied per second)

track_color = gray

# Debug variables
track_maker = []
show_debug = True  # Toggle with D key

# Load car image
try:
    car_image = pygame.image.load("car.jpeg").convert_alpha()
    car_image = pygame.transform.scale(car_image, (car_width, car_height))
except pygame.error:
    # Create a fallback car if image not found
    car_image = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
    pygame.draw.polygon(car_image, (255, 0, 0), [(0, car_height), (car_width//2, 0), (car_width, car_height)])

# Create car mask for collision detection
car_mask = pygame.mask.from_surface(car_image)


def load_arrays_from_file(filepath):
    """Loads left_boundary and right_boundary arrays from a text file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Split the content into left and right boundary strings
        left_str, right_str = content.split('\n')

        # Use ast.literal_eval to safely convert the strings to lists of tuples
        left_boundary = ast.literal_eval(left_str.split("=")[1].strip())
        right_boundary = ast.literal_eval(right_str.split("=")[1].strip())

        print("inside load array")
        return left_boundary, right_boundary

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None, None
    except (SyntaxError, ValueError) as e:
        print(f"Error: Invalid file format. {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None

left_boundary, right_boundary = load_arrays_from_file("track_1.txt")
all_boundaries = left_boundary + right_boundary










"""
FUNCTIONS
"""

# Function to draw the track
def draw_track():
        
    if len(left_boundary) > 1:
        pygame.draw.lines(screen, track_color, True, left_boundary, 2)

    if len(right_boundary) > 1:
        pygame.draw.lines(screen, track_color, True, right_boundary, 2)
    
        
# Function to rotate the car image
def rotate_car(image, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image


# Add these lines near your existing draw functions to visualize collision boxes and lines
def draw_car_collision_box(screen, car_x, car_y, car_angle):
    """Draw the car's collision box/lines for visualization"""
    car_corners = [
        (-car_width//2, -car_height//2),  # Top-left
        (car_width//2, -car_height//2),   # Top-right
        (car_width//2, car_height//2),    # Bottom-right
        (-car_width//2, car_height//2)    # Bottom-left
    ]
    
    # Rotate car corners
    angle_rad = math.radians(-car_angle) # car angle negetive is required due to coordinate system
    rotated_corners = []
    for x, y in car_corners:
        rx = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        ry = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        rotated_corners.append((car_x + rx, car_y + ry))
    
    # Draw the car's collision box
    for i in range(len(rotated_corners)):
        start_point = rotated_corners[i]
        end_point = rotated_corners[(i+1) % len(rotated_corners)]
        pygame.draw.line(screen, (255, 0, 0), start_point, end_point, 2)  # Red lines for car box


def draw_active_collision_segments(screen, car_x, car_y, car_angle, boundary_points, check_radius=150):
    """Draw only the track segments near the car that are being checked for collision"""
    if len(boundary_points) < 2:
        return
    
    # Draw only segments within check_radius of the car
    for i in range(len(boundary_points) - 1):
        p1 = boundary_points[i]
        p2 = boundary_points[i+1]
        
        # If either point is within radius, draw the segment
        dist1 = math.hypot(p1[0] - car_x, p1[1] - car_y)
        dist2 = math.hypot(p2[0] - car_x, p2[1] - car_y)
        
        if dist1 < check_radius or dist2 < check_radius:
            pygame.draw.line(screen, yellow , p1, p2, 3)  # Yellow lines for active segments


def check_boundary_collision(car_x, car_y, car_angle, boundary_points):
    """
    Check if the car has collided with any line segment formed by connecting
    the boundary points in sequence.
    
    Args:
        car_x, car_y: Center position of the car
        car_angle: Rotation angle of the car in degrees
        boundary_points: List of (x,y) points defining a boundary
    
    Returns:
        bool: True if car has collided with any boundary line, False otherwise
    """
    if len(boundary_points) < 2:
        return False  # Need at least 2 points to form a line
    
    # Create a rotated hitbox for the car
    car_corners = [
        (-car_width//2, -car_height//2),  # Top-left
        (car_width//2, -car_height//2),   # Top-right
        (car_width//2, car_height//2),    # Bottom-right
        (-car_width//2, car_height//2)    # Bottom-left
    ]        
    
    # Rotate car corners
    angle_rad = math.radians(-car_angle) # car angle negetive is required due to coordinate system
    rotated_corners = []
    for x, y in car_corners:
        rx = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        ry = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        rotated_corners.append((car_x + rx, car_y + ry))
    
    # Create car edges from corners
    car_edges = []
    for i in range(len(rotated_corners)):
        car_edges.append((rotated_corners[i], rotated_corners[(i+1) % len(rotated_corners)]))
    
    # Check for line intersections between car edges and boundary lines
    for i in range(len(boundary_points) - 1):
        boundary_p1 = boundary_points[i]
        boundary_p2 = boundary_points[i+1]
        
        for car_edge in car_edges:
            car_p1, car_p2 = car_edge
            
            if line_segments_intersect(car_p1, car_p2, boundary_p1, boundary_p2):
                # Visualize the collision point
                midpoint_x = (car_p1[0] + car_p2[0]) / 2
                midpoint_y = (car_p1[1] + car_p2[1]) / 2
                pygame.draw.circle(screen, (255, 0, 0), (int(midpoint_x), int(midpoint_y)), 5)
                return True  # Collision detected
    
    return False  # No collision


def line_segments_intersect(p1, p2, p3, p4):
    """
    Check if two line segments (p1-p2) and (p3-p4) intersect.
    
    Args:
        p1, p2: Points defining first line segment as (x,y) tuples
        p3, p4: Points defining second line segment as (x,y) tuples
    
    Returns:
        bool: True if the segments intersect, False otherwise
    """
    # Extract coordinates
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    # Calculate direction vectors
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3
    
    # Calculate denominator for intersection formulas
    denominator = (dy2 * dx1 - dx2 * dy1)
    
    # Check if lines are parallel (denominator near zero)
    if abs(denominator) < 1e-10:
        return False
    
    # Calculate parameters for intersection point
    ua = ((dx2 * (y1 - y3)) - (dy2 * (x1 - x3))) / denominator
    ub = ((dx1 * (y1 - y3)) - (dy1 * (x1 - x3))) / denominator
    
    # Check if intersection point is within both line segments
    return (0 <= ua <= 1) and (0 <= ub <= 1)


def draw_HUD_info(screen, has_collided):
    """Display HUD in the top-left corner"""
    collision_text = font.render(f'COLLISION: {str(has_collided).upper()}', True, (255, 0, 0))  # Red text for collision

    
    screen.blit(collision_text, (10, 10))  # Position in top-left corner



















"""
MAIN GAME LOOP
"""

running = True
last_time = pygame.time.get_ticks() / 1000.0  # Starting time in seconds

while running:
    # Calculate delta time for frame-rate independence
    current_time = pygame.time.get_ticks() / 1000.0  # Current time in seconds
    delta_time = current_time - last_time  # Time elapsed since last frame

    last_time = current_time
    
    # Cap delta_time to prevent physics issues if game freezes momentarily
    if delta_time > 0.1:
        delta_time = 0.1
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                show_debug = not show_debug
            if event.key == pygame.K_r:
                car_x = screen_width/2
                car_y = screen_height/2
                car_speed = 0
                car_angle = 0
    
    # Get pressed keys
    pressed_keys = pygame.key.get_pressed()
    
    # Apply friction (scaled by delta_time)
    car_speed /= pow(car_friction, delta_time)
    
    # Handle steering (scaled by delta_time)
    if pressed_keys[pygame.K_LEFT]:
        car_angle += car_steering_speed * delta_time
    if pressed_keys[pygame.K_RIGHT]:
        car_angle -= car_steering_speed * delta_time
    
    # Handle acceleration/braking (scaled by delta_time)
    if pressed_keys[pygame.K_UP]:
        car_speed += car_acceleration * delta_time
        car_speed = min(car_speed, car_max_speed)
    if pressed_keys[pygame.K_DOWN]:
        car_speed -= car_acceleration * delta_time
        car_speed = max(car_speed, -car_max_speed/2)  # Reverse is slower
    
    # Calculate movement vector based on car angle and speed
    movement_x = car_speed * delta_time * math.cos(math.radians(car_angle))
    movement_y = car_speed * delta_time * -math.sin(math.radians(car_angle))
    
    # Calculate new position
    new_car_x = car_x + movement_x
    new_car_y = car_y + movement_y
    
    left_collision = check_boundary_collision(car_x, car_y, car_angle, left_boundary)
    right_collision = check_boundary_collision(car_x, car_y, car_angle, right_boundary)
    collision = True if left_collision or right_collision else False
    
    # update car position
    car_x = new_car_x
    car_y = new_car_y

    
    # Add point to track_maker if 1 key is pressed
    if pressed_keys[pygame.K_1]:
        track_maker.append((car_x, car_y))
        print("Added point:", (car_x, car_y))
    
    # Print track_maker points if 2 key is pressed
    if pressed_keys[pygame.K_2]:
        print("track_points =", track_maker)
    
    
    # Debug info
    if show_debug:
        print(f"FPS: {clock.get_fps():.1f}, Position: ({car_x:.1f}, {car_y:.1f}), Angle: {car_angle:.1f}, Speed: {car_speed:.1f}")
        if collision:
            print("collision")

    # Clear screen
    screen.fill(white)
    
    # Draw track
    draw_track()
    
    # Draw car
    rotated_car_image = rotate_car(car_image, car_angle)
    car_rect = rotated_car_image.get_rect(center=(car_x, car_y))
    screen.blit(rotated_car_image, car_rect)

    if show_debug:
        # Draw car collision box
        draw_car_collision_box(screen, car_x, car_y, car_angle)

        # Draw track segments that are near the car
        draw_active_collision_segments(screen, car_x, car_y, car_angle, left_boundary, check_radius=200)
        draw_active_collision_segments(screen, car_x, car_y, car_angle, right_boundary, check_radius=200)

    # Draw on HUD values
    draw_HUD_info(screen, collision)

    # Update display
    pygame.display.flip()
    
    # Cap the frame rate (still useful for efficiency)
    clock.tick(target_fps)

# Print final track points if any were created
if track_maker:
    print("Final track points:")
    print(track_maker)

# Quit Pygame
pygame.quit()

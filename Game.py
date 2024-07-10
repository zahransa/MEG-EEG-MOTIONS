import pygame
import random
import time
import serial
import csv

# Initialize Pygame
pygame.init()

# Initialize Serial Communication
arduino_port = 'COM6'  # Update with your Arduino port
baud_rate = 115200

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except Exception as e:
    print(f"Could not connect to Arduino: {e}")
    ser = None

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)
WALL_COLOR = (0, 0, 0)
FOOD_COLOR = (0, 255, 0)
BIRD_COLOR = (255, 165, 0)
BEAK_COLOR = (255, 0, 0)
BUTTON_COLOR = (0, 0, 255)
TEXT_COLOR = (0, 0, 0)
RED_HOLE_COLOR = (255, 0, 0)
CLOSE_BUTTON_COLOR = (255, 0, 0)  # Red color for close button
CLOSE_BUTTON_TEXT_COLOR = (0, 0, 0)  # Black color for text on close button

# Game settings
wall_x = SCREEN_WIDTH // 2
wall_y = 100
wall_width = 50
wall_height = 400
hole_height = 100
hole_y = wall_y
hole_speed = 10
bird_x = SCREEN_WIDTH - 80
bird_y = SCREEN_HEIGHT // 2
food_speed = 10
foods_in_motion = []  # List to store all foods in motion
computer_food_in_motion = False
button_pressed = False
score = 0

# Timing
last_shot_time = 0
last_computer_shot_time = 0  # Track last time computer shot
shot_interval = 3
hole_y_direction = 1
speed_setting = 'normal'
vibro_tactile_feedback = False
beak_open = True
beak_open_time = 0

# Trials settings
total_trials = 100
player_shot_percentage = 80  # 80% shots by player
computer_shot_percentage = 20  # 20% shots by computer
player_shots = total_trials * player_shot_percentage // 100
computer_shots = total_trials * computer_shot_percentage // 100
current_trial = 0
remaining_player_shots = player_shots
remaining_computer_shots = computer_shots

# Message variables
message_text = ""
message_display_start_time = 0
message_display_duration = 2

# Close button dimensions and position
CLOSE_BUTTON_WIDTH = 100
CLOSE_BUTTON_HEIGHT = 50
close_button_x = bird_x - 50  # Center the button under the bird
close_button_y = bird_y + 50

# CSV file setup
csv_file = 'player_responses.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Response'])  # Write header

# Functions
def log_response(response):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.time(), response])

def draw_wall_with_hole(screen, wall_x, wall_y, hole_y, hole_height):
    pygame.draw.rect(screen, WALL_COLOR, (wall_x, wall_y, wall_width, wall_height))
    pygame.draw.rect(screen, RED_HOLE_COLOR, (wall_x, hole_y, wall_width, hole_height))

def draw_bird(screen, x, y, beak_open):
    pygame.draw.ellipse(screen, BIRD_COLOR, (x - 30, y - 20, 60, 40))
    pygame.draw.circle(screen, (0, 0, 0), (x - 15, y - 10), 5)
    if beak_open:
        pygame.draw.polygon(screen, BEAK_COLOR, [(x - 30, y), (x - 50, y - 10), (x - 50, y + 10)])
    else:
        pygame.draw.polygon(screen, BEAK_COLOR, [(x - 30, y), (x - 40, y - 5), (x - 40, y + 5)])

    # Draw close mouth button
    pygame.draw.rect(screen, CLOSE_BUTTON_COLOR,
                     (close_button_x, close_button_y, CLOSE_BUTTON_WIDTH, CLOSE_BUTTON_HEIGHT))
    font = pygame.font.SysFont(None, 24)
    text_surface = font.render("Close", True, CLOSE_BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(
        center=(close_button_x + CLOSE_BUTTON_WIDTH // 2, close_button_y + CLOSE_BUTTON_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def display_text(screen, text, x, y):
    font = pygame.font.SysFont(None, 36)
    rendered_text = font.render(text, True, TEXT_COLOR)
    screen.blit(rendered_text, (x, y))

def adjust_speed(setting):
    global hole_speed, hole_height
    if setting == 'easy':
        hole_speed = 3
        hole_height = 150
    elif setting == 'normal':
        hole_speed = 6
        hole_height = 100
    elif setting == 'hard':
        hole_speed = 10
        hole_height = 50

# Set speed based on current setting
adjust_speed(speed_setting)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Feed the Bird Game")

def send_vibration_intensity(intensity):
    if ser and ser.is_open:
        ser.write(f"{intensity}\n".encode())
        print(f"Sent intensity: {intensity}")

def handle_player_shoot():
    global foods_in_motion, last_shot_time, vibro_tactile_feedback
    food_x = 100
    food_y = bird_y
    foods_in_motion.append({'x': food_x, 'y': food_y, 'passing_hole': False, 'player_shot': True})
    last_shot_time = time.time()
    vibro_tactile_feedback = True
    vibration_intensity = 4  # Fixed intensity
    send_vibration_intensity(vibration_intensity)

def handle_computer_shoot():
    global foods_in_motion, last_computer_shot_time
    food_x = 100
    food_y = bird_y
    foods_in_motion.append({'x': food_x, 'y': food_y, 'passing_hole': False, 'player_shot': False})
    last_computer_shot_time = time.time()
    print("Computer shot")

def update_food_position():
    global foods_in_motion, score, message_text
    for food in foods_in_motion[:]:
        pygame.draw.circle(screen, FOOD_COLOR, (food['x'], food['y']), 10)
        food['x'] += food_speed
        if food['x'] >= wall_x:
            if not food['passing_hole'] and hole_y <= food['y'] <= hole_y + hole_height:
                food['passing_hole'] = True  # Food has successfully passed through the hole
            elif not food['passing_hole']:
                # Food hits the wall
                if food['player_shot']:
                    message_text = "Hit the Wall!"
                    score -= 5
                foods_in_motion.remove(food)
        if food['passing_hole']:
            if food['x'] >= bird_x - 30:
                if food['player_shot']:
                    if beak_open:
                        message_text = "Fed the Bird!"
                        score += 10
                    else:
                        message_text = "Missed the Bird!"
                        score -= 5
                else:
                    if beak_open:
                        message_text = "Computer Fed the Bird!"
                        score -= 5
                    else:
                        message_text = "Player Blocked the Bird!"
                foods_in_motion.remove(food)

# Main game loop
running = True
food_x = 0
food_y = bird_y
player_can_shoot = True  # Flag to control player shooting ability

while running:
    screen.fill(BACKGROUND_COLOR)
    hole_y += hole_speed * hole_y_direction
    if hole_y <= wall_y:
        hole_y_direction = 1
    elif hole_y + hole_height >= wall_y + wall_height:
        hole_y_direction = -1
        if not foods_in_motion and current_trial < total_trials and remaining_computer_shots > 0:
            handle_computer_shoot()
            remaining_computer_shots -= 1
    draw_wall_with_hole(screen, wall_x, wall_y, hole_y, hole_height)
    draw_bird(screen, bird_x, bird_y, beak_open)
    pygame.draw.rect(screen, BUTTON_COLOR, (50, SCREEN_HEIGHT - 100, 100, 50))
    display_text(screen, "Shoot", 60, SCREEN_HEIGHT - 90)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if shoot button is clicked
            if 50 <= pygame.mouse.get_pos()[0] <= 150 and SCREEN_HEIGHT - 100 <= pygame.mouse.get_pos()[1] <= SCREEN_HEIGHT - 50:
                handle_player_shoot()
                current_trial += 1
                remaining_player_shots -= 1
            # Check if close mouth button is clicked
            elif close_button_x <= pygame.mouse.get_pos()[0] <= close_button_x + CLOSE_BUTTON_WIDTH and close_button_y <= pygame.mouse.get_pos()[1] <= close_button_y + CLOSE_BUTTON_HEIGHT:
                beak_open = False  # Close the bird's mouth

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button release
                beak_open = True  # Open the bird's mouth

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                handle_player_shoot()
                current_trial += 1
                remaining_player_shots -= 1
            elif event.key == pygame.K_RIGHT:
                beak_open = False  # Close the bird's mouth
            elif event.key == pygame.K_UP:
                log_response(1)  # Log 1 to CSV
            elif event.key == pygame.K_DOWN:
                log_response(0)  # Log 0 to CSV

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                beak_open = True  # Open the bird's mouth

    update_food_position()

    display_text(screen, f"Score: {score}", 650, 50)
    display_text(screen, f"Trials: {current_trial}/{total_trials}", 650, 100)
    if message_text:
        display_text(screen, message_text, 300, 50)
        if time.time() - message_display_start_time > message_display_duration:
            message_text = ""

    pygame.display.flip()
    pygame.time.Clock().tick(30)

if ser:
    ser.close()

pygame.quit()

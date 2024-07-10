# Feed the Bird Game
# Overview
Feed the Bird is an interactive game built using Python and Pygame, simulating a scenario where the player and computer take turns to shoot food towards a bird. The goal is to feed the bird by getting the food through a moving hole in a wall. The game also incorporates serial communication with an Arduino for providing vibro-tactile feedback.

# How to Play
In Feed the Bird, you control the bird's feeding process by shooting food and closing the bird's beak. The game involves both player and computer taking turns to shoot food. The bird's beak can be controlled to catch or miss the food, adding to the challenge.

C# ontrols
Mouse Click: Click on the "Shoot" button to shoot food towards the bird.
Left Arrow Key: Shoot food using the keyboard.
Right Arrow Key: Close the bird's beak.
Mouse Click on the "Close" Button: Close the bird's beak using the button below the bird.
Up Arrow Key: Log response "1" (custom functionality).
Down Arrow Key: Log response "0" (custom functionality).
Game Elements
Bird: Positioned on the right side of the screen, it opens and closes its beak.
Wall with Hole: A vertical wall with a moving hole through which food must pass to reach the bird.
Food: Objects shot from the left side of the screen towards the bird.
Shoot Button: A button at the bottom left of the screen for shooting food.
Close Button: A button below the bird to close its beak.

# Game Features
Vibro-Tactile Feedback: When the player shoots food, an intensity signal is sent to an Arduino via serial communication to provide tactile feedback.
Dynamic Difficulty: The speed and size of the hole in the wall can be adjusted to change the game's difficulty.
Score Tracking: Points are awarded or deducted based on successful feeding or missing the bird.
Trial Management: The game tracks the number of shots taken by the player and the computer, with predefined shot percentages.
Serial Communication
The game uses serial communication to send signals to an Arduino for vibro-tactile feedback. Ensure the correct port (COM6 in the script) and baud rate (115200) are set up for your Arduino.

# CSV Logging
Player responses are logged in a CSV file (player_responses.csv). Each log entry includes a timestamp and a response value, useful for further analysis or study purposes.

Setup and Running the Game
Prerequisites
Python 3.x
Pygame library
Serial library (pyserial)
An Arduino connected to the specified port
Installation
Install Python 3.x from Python.org.
Install the required Python libraries:
sh
Copy code
pip install pygame pyserial
Running the Game
Connect your Arduino to the specified port.
Run the Python script:
sh
Copy code
python feed_the_bird_game.py

# Customization
# Adjusting Game Speed and Difficulty
Modify the adjust_speed function to change the speed and size of the hole in the wall. This function takes a speed_setting parameter which can be set to 'easy', 'normal', or 'hard'.

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
# Changing the Number of Trials
Update the total_trials variable to set the number of trials for the game. The player and computer shot percentages can also be adjusted:

total_trials = 100
player_shot_percentage = 80  # 80% shots by player
computer_shot_percentage = 20  # 20% shots by computer
Closing the Game

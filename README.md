# Road Rage Game
## Group Members
- Mehrab Muhtasim Sayem
- Abrar Syed Chowdhury
- Noushin Fariha Ronok
## Overview
This project is a road crossing game developed using OpenGL and Python. The game is designed for a computer graphics course and demonstrates various graphics techniques such as drawing shapes, handling user input, and managing game states.

## Features
- **Player Movement:** The player can move up, down, left, and right using the `W`, `A`, `S`, and `D` keys.
- **Vehicle Spawning:** Different types of vehicles (cars, buses, bikes) spawn at random intervals and move across the screen.
- **Collision Detection:** The game detects collisions between the player and vehicles, ending the game if a collision occurs.
- **Score System:** The player earns points by crossing roads.
- **Pause and Restart:** The game can be paused with the `P` key and restarted with the `R` key after a game over.

## Installation
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/mehrab-m-sayem/road-rage-game.git
   cd road-rage-game
   ```

2. **Install Dependencies:**
   Ensure you have Python installed. Then, install the required Python packages:
   ```sh
   pip install PyOpenGL PyOpenGL_accelerate numpy
   ```

## Running the Game
To run the game, execute the following command:
```sh
python main.py
```

## Controls
- **W:** Move up
- **A:** Move left
- **S:** Move down
- **D:** Move right
- **P:** Pause the game
- **R:** Restart the game after a game over

## Code Structure
- **main.py:** The main script that initializes and runs the game.
- **Game Class:** Contains the game logic, including drawing functions, vehicle spawning, collision detection, and score management.
- **OpenGL Functions:** Utilizes OpenGL functions to draw shapes and handle rendering.

## Dependencies
- **PyOpenGL:** Python bindings for OpenGL.
- **numpy:** Library for numerical operations.

## Acknowledgements
This project was developed as part of a computer graphics course (CSE423) of BRAC University.



---

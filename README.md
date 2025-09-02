# AeroPizza

A fast-paced 2D car combat game where you control a pizza-slice-shaped car and battle against other players or AI opponents. The game is built with Pygame and features realistic physics, different game modes, and power-ups.

## Features

*   **Two Game Modes:**
    *   **Free Play:** A chaotic battle mode where the goal is to destroy as many opponents as possible.
    *   **Race Mode:** A classic race where the goal is to complete the track as fast as possible.
*   **Single-player, Two-player, and AI:** Play against a friend or challenge the AI with different difficulty levels.
*   **Physics-based Gameplay:** The game uses a physics engine that simulates realistic car handling, collisions, and damage.
*   **Combat System:** Equip your car with a cannon to shoot at your opponents.
*   **Health Pickups:** Grab health pickups to repair your car and stay in the game.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/user/repository.git
    ```
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the game:**
    ```bash
    python main.py
    ```

## How to Play

### Controls

*   **Player 1:**
    *   **Accelerate:** UP Arrow
    *   **Brake:** DOWN Arrow
    *   **Turn Left:** LEFT Arrow
    *   **Turn Right:** RIGHT Arrow
    *   **Shoot:** SPACE
*   **Player 2:**
    *   **Accelerate:** Z
    *   **Brake:** S
    *   **Turn Left:** Q
    *   **Turn Right:** D
    *   **Shoot:** LEFT CTRL

### Objective

*   **Free Play:** Destroy as many opponents as possible to increase your score.
*   **Race Mode:** Complete the track as fast as possible.

## Code Structure

*   `main.py`: The main entry point of the game. It contains the main game loop and handles the game state.
*   `car.py`: Defines the `Car` and `Bullet` classes, which represent the cars and bullets in the game.
*   `constants.py`: Contains all the constants used in the game, such as screen dimensions, colors, and car parameters.
*   `collision_utils.py`: Provides functions for collision detection and resolution using the Separating Axis Theorem (SAT).
*   `wall.py`: Defines the `Wall` class, which represents the walls of the track.
*   `health_pickup.py`: Defines the `HealthPickup` class, which represents the health pickups in the game.
*   `aer0pizza.py`: An older, single-file version of the game.
*   `requirements.txt`: A list of the Python dependencies required to run the game.
*   `assets/`: This directory contains the sound assets for the game.

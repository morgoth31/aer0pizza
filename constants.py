# --- Game Constants ---
SCREEN_WIDTH = 1800  # Screen width in pixels
SCREEN_HEIGHT = 1000  # Screen height in pixels
FPS = 60  # Frames per second
GAME_TITLE = "AeroPizza"  # Game title

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (200, 200, 200)  # Track color
WALL_COLOR = (70, 70, 70)  # Wall color
MAGENTA = (255, 0, 255)  # Color for AI debugging
BULLET_COLOR = (255, 255, 0)  # Yellow for bullets

# --- Car Parameters ---
CAR_WIDTH = 40  # Width of the car's base
CAR_LENGTH = 60  # Length of the car
CAR_MASS = 100  # Mass of the car in kg
CAR_INERTIA = 500  # Moment of inertia for rotation
ENGINE_FORCE = 50000  # Engine force in Newtons
BRAKE_FORCE = 7000  # Braking force
FRICTION_COEFF = 0.8  # Friction coefficient for tire friction
DRAG_COEFF = 0.5  # Drag coefficient for air resistance
ANGULAR_ACCELERATION_MAGNITUDE = 300000  # Magnitude of angular acceleration for turns
MAX_HP = 30  # Maximum health points

# --- Cannon Parameters ---
BULLET_SPEED = 500  # Speed of the bullet
BULLET_RADIUS = 3  # Radius of the bullet
BULLET_DAMAGE = 10  # Damage inflicted by a bullet
CANNON_COOLDOWN = 0.5  # Cooldown time for the cannon in seconds
MAX_BULLETS = 6  # Maximum number of bullets a car can have

# --- Collision Parameters ---
COLLISION_ELASTICITY = 0.7  # Coefficient of restitution (0 = no bounce, 1 = perfect bounce)
COLLISION_FRICTION = 0.5  # Friction coefficient during collision
DAMAGE_FACTOR = 0.01  # Base factor for calibrating damage
COLLISION_DAMAGE_MULTIPLIER = 5.0  # Damage multiplier for car-on-car impacts
WALL_DAMAGE_FACTOR = 500.0  # Damage taken when colliding with walls
MIN_IMPACT_FORCE_FOR_DAMAGE = 500.0  # Minimum impact force threshold to inflict damage
FRONT_IMPACT_THRESHOLD = 0.7  # Dot product threshold to determine a "front" impact

# --- Game Parameters ---
DISABLED_DURATION = 3.0  # Duration in seconds a car is disabled after destruction
SCORE_INCREMENT = 1  # Points gained when a car is destroyed
HEALTH_PICKUP_SPAWN_INTERVAL = 10.0  # Frequency of health pickup appearance in seconds
HEALTH_PICKUP_MIN_HP = 5  # Minimum health points recovered by a pickup
HEALTH_PICKUP_MAX_HP = 15  # Maximum health points recovered by a pickup
HEALTH_PICKUP_RADIUS = 15  # Radius of the health pickup circle
HEALTH_PICKUP_COLLISION_RATIO = 0.5  # Ratio of the health pickup's radius for collision detection

# --- Game Modes ---
GAME_MODE_FREE_PLAY = "free_play"
GAME_MODE_RACE = "race"

# --- AI Difficulty ---
DIFFICULTY_EASY = "facile"
DIFFICULTY_MEDIUM = "moyen"
DIFFICULTY_HARD = "difficile"
DIFFICULTY_PRO = "pro"

AI_SPEED_MULTIPLIERS = {
    DIFFICULTY_EASY: 0.6,
    DIFFICULTY_MEDIUM: 0.8,
    DIFFICULTY_HARD: 0.9,
    DIFFICULTY_PRO: 1.0,  # Pro AI is as fast as player
}

# --- Display Parameters ---
COORD_FONT_SIZE = 18  # Font size for coordinates

# --- Sounds ---
# Path to sound files (adapt by user)
# Make sure these .mp3 files are in the 'assets' directory relative to the script
SOUND_COLLISION_PATH = "assets/collision.mp3"  # Collision sound
SOUND_MENU_SELECT_PATH = "assets/menu_select.mp3"  # Menu selection sound
SOUND_PICKUP_PATH = "assets/pickup.mp3"  # Health pickup sound

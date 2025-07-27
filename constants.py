# --- Game Constants ---
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000
FPS = 60
GAME_TITLE = "Jeu de Voiture 2D - Prototype Amélioré 4"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (200, 200, 200) # Track color - Changed to a lighter gray for better visibility of red AI cars
WALL_COLOR = (70, 70, 70) # Wall color

# --- Car Parameters ---
CAR_WIDTH = 40  # Largeur de la base de la "part de pizza"
CAR_LENGTH = 60 # Longueur de la "part de pizza" (du centre de la base à la pointe)
CAR_MASS = 100 # kg
CAR_INERTIA = 500 # Moment d'inertie pour la rotation (kg * m^2)
ENGINE_FORCE = 50000 # Force du moteur en Newtons
BRAKE_FORCE = 7000 # Force de freinage
FRICTION_COEFF = 0.8 # Coefficient de frottement (pour la friction des pneus)
DRAG_COEFF = 0.5 # Coefficient de traînée (résistance de l'air)
ANGULAR_ACCELERATION_MAGNITUDE = 300000 # Magnitude de l'accélération angulaire pour les virages

MAX_HP = 30 # Points de vie maximum

# --- Collision Parameters ---
COLLISION_ELASTICITY = 0.7 # Coefficient de restitution (0 = pas de rebond, 1 = rebond parfait)
COLLISION_FRICTION = 0.5 # Coefficient de frottement lors de la collision
DAMAGE_FACTOR = 0.01 # Facteur de base pour calibrer les dégâts (ajuster selon les tests)
COLLISION_DAMAGE_MULTIPLIER = 5.0 # Multiplicateur de dégâts pour les impacts entre voitures
WALL_DAMAGE_FACTOR = 500.0 # Dégâts subis lors de la collision avec les bords
MIN_IMPACT_FORCE_FOR_DAMAGE = 500.0 # Increased threshold - Seuil minimum de force d'impact pour infliger des dégâts
FRONT_IMPACT_THRESHOLD = 0.7 # Seuil du produit scalaire pour déterminer un impact "de face"

# --- Game Parameters ---
DISABLED_DURATION = 3.0 # Durée en secondes pendant laquelle une voiture est désactivée après destruction
SCORE_INCREMENT = 1 # Points gagnés lorsqu'une voiture est détruite
HEALTH_PICKUP_SPAWN_INTERVAL = 10.0 # Fréquence d'apparition des bonus de vie en secondes
HEALTH_PICKUP_MIN_HP = 5 # Points de vie minimum récupérés par un bonus
HEALTH_PICKUP_MAX_HP = 15 # Points de vie maximum récupérés par un bonus
HEALTH_PICKUP_RADIUS = 15 # Rayon du cercle du bonus de vie

# --- Display Parameters ---
COORD_FONT_SIZE = 18 # NOUVEAU: Taille de la police pour les coordonnées

# --- Sounds ---
# Path to sound files (adapt by user)
# Make sure these .mp3 files are in the 'assets' directory relative to the script
SOUND_ENGINE_PATH = "assets/engine_loop.mp3" # Looping engine sound
SOUND_COLLISION_PATH = "assets/collision.mp3" # Collision sound
SOUND_MENU_SELECT_PATH = "assets/menu_select.mp3" # Menu selection sound
SOUND_PICKUP_PATH = "assets/pickup.mp3" # Health pickup sound

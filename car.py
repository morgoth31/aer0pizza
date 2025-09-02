import pygame
import math
import random
from constants import * # Import all constants
from wall import Wall # Import Wall class from wall.py
from collision_utils import resolve_collision # Import collision resolution function

# --- Classe Bullet ---
class Bullet(pygame.sprite.Sprite):
    """
    Represents a bullet fired by a car.
    """
    def __init__(self, x, y, angle, owner_car_color):
        """
        Initializes a new Bullet object.

        Args:
            x (int): The x-coordinate of the bullet's starting position.
            y (int): The y-coordinate of the bullet's starting position.
            angle (float): The angle in degrees at which the bullet is fired.
            owner_car_color (tuple): The color of the car that fired the bullet.
        """
        super().__init__()
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, -BULLET_SPEED).rotate(angle)
        self.radius = BULLET_RADIUS
        self.color = BULLET_COLOR
        self.damage = BULLET_DAMAGE
        self.owner_car_color = owner_car_color
        # Rect plus précis pour la collision
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)


    def update(self, dt):
        """
        Updates the bullet's position.

        Args:
            dt (float): The time delta since the last frame.
        """
        self.position += self.velocity * dt
        self.rect.center = (int(self.position.x), int(self.position.y))

    def draw(self, screen):
        """
        Draws the bullet on the screen.

        Args:
            screen (pygame.Surface): The screen to draw the bullet on.
        """
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.position.x), int(self.position.y)), self.radius, 1) # Contour

# --- Classe Car ---
class Car(pygame.sprite.Sprite):
    """
    Represents a car in the game.
    """
    def __init__(self, x, y, angle=0, color=BLUE, is_player=True, game_mode=GAME_MODE_FREE_PLAY, difficulty=None):
        """
        Initializes a new Car object.

        Args:
            x (int): The x-coordinate of the car's starting position.
            y (int): The y-coordinate of the car's starting position.
            angle (float, optional): The initial angle of the car in degrees. Defaults to 0.
            color (tuple, optional): The color of the car. Defaults to BLUE.
            is_player (bool, optional): Whether the car is controlled by a player. Defaults to True.
            game_mode (str, optional): The game mode. Defaults to GAME_MODE_FREE_PLAY.
            difficulty (str, optional): The AI difficulty. Defaults to None.
        """
        super().__init__()
        print(f"Creating Car: Color={color}, Player={is_player}, Initial Pos=({x}, {y}), Mode={game_mode}, Difficulty={difficulty}")
        self.original_image = self.create_pizza_slice_surface(CAR_WIDTH, CAR_LENGTH, color)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.initial_position = pygame.math.Vector2(x, y) # For respawn
        self.initial_angle = angle # For respawn

        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = angle  # Angle in degrees (0 = up, 90 = right)
        self.angular_velocity = 0 # Angular velocity in degrees per second

        self.mass = CAR_MASS
        self.inertia = CAR_INERTIA
        self.hp = MAX_HP
        self.is_player = is_player # True if controlled by player, False if AI
        self.score = 0 # Car score

        self.color = color
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.speed_multiplier = 1.0
        if not self.is_player and self.difficulty:
            self.speed_multiplier = AI_SPEED_MULTIPLIERS.get(self.difficulty, 1.0) # Default to 1.0 if difficulty not found

        # Flags de contrôle
        self.accelerating = False
        self.braking = False
        self.turning_left = False
        self.turning_right = False

        # Cannon properties
        self.can_fire = True
        self.fire_cooldown_timer = 0.0
        self.fire_cooldown = CANNON_COOLDOWN
        self.bullets_remaining = MAX_BULLETS  # Ajout du compteur de balles
        self.max_bullets = MAX_BULLETS

        # État de désactivation après destruction
        self.is_disabled = False
        self.disabled_timer = 0.0

        # Points de la forme de la "part de pizza" (relatifs au centre de la voiture)
        self.base_points = [
            pygame.math.Vector2(0, -CAR_LENGTH / 2),  # Pointe avant (index 0)
            pygame.math.Vector2(-CAR_WIDTH / 2, CAR_LENGTH / 2), # Bas-gauche (index 1)
            pygame.math.Vector2(CAR_WIDTH / 2, CAR_LENGTH / 2)   # Bas-droite (index 2)
        ]
        self.rotated_points = [pygame.math.Vector2(0,0), pygame.math.Vector2(0,0), pygame.math.Vector2(0,0)] # Points après rotation

        # Zones de dégâts avec résistances
        self.damage_zones = {
            "front": {"resistance": 1.5},
            "sides": {"resistance": 0.8},
            "rear": {"resistance": 1.0}
        }

        # Sons
        # self.engine_sound = None # REMOVED: Engine sound
        self.collision_sound = None
        self.pickup_sound = None
        try:
            # self.engine_sound = pygame.mixer.Sound(SOUND_ENGINE_PATH) # REMOVED
            # self.engine_sound.set_volume(0.3) # REMOVED
            if self.is_player: # Only player cars had engine sound
                pass # self.engine_sound.play(-1) # REMOVED
        except pygame.error as e:
            print(f"Erreur de chargement du son du moteur: {e}")
        
        try:
            self.collision_sound = pygame.mixer.Sound(SOUND_COLLISION_PATH)
            self.collision_sound.set_volume(0.5)
        except pygame.error as e:
            print(f"Erreur de chargement du son de collision: {e}")

        try:
            self.pickup_sound = pygame.mixer.Sound(SOUND_PICKUP_PATH)
            self.pickup_sound.set_volume(0.6)
        except pygame.error as e:
            print(f"Erreur de chargement du son de ramassage: {e}")

        # Race mode specific
        self.current_waypoint_index = 0


    def create_pizza_slice_surface(self, width, length, color):
        """
        Creates a Pygame surface with the shape of a pizza slice.

        Args:
            width (int): The width of the pizza slice's base.
            length (int): The length of the pizza slice.
            color (tuple): The color of the pizza slice.

        Returns:
            pygame.Surface: A Pygame surface with the pizza slice shape.
        """
        max_dim = max(width, length) * 2
        surface = pygame.Surface((max_dim, max_dim), pygame.SRCALPHA)
        
        center_x, center_y = max_dim / 2, max_dim / 2
        
        points = [
            (center_x, center_y - length / 2),
            (center_x - width / 2, center_y + length / 2),
            (center_x + width / 2, center_y + length / 2)
        ]
        pygame.draw.polygon(surface, color, points)
        return surface

    def handle_input(self, keys, player_num=1):
        """
        Handles keyboard input to control the car.

        Args:
            keys (pygame.key.get_pressed): The current state of the keyboard.
            player_num (int, optional): The player number (1 or 2). Defaults to 1.

        Returns:
            Bullet or None: A new Bullet object if the car fires, otherwise None.
        """
        if self.is_disabled: # Ne pas traiter les inputs si la voiture est désactivée
            self.accelerating = self.braking = self.turning_left = self.turning_right = False
            return None # No bullet fired

        self.accelerating = False
        self.braking = False
        self.turning_left = False
        self.turning_right = False
        
        bullet = None

        if player_num == 1:
            if keys[pygame.K_UP]:
                self.accelerating = True
            if keys[pygame.K_DOWN]:
                self.braking = True
            if keys[pygame.K_LEFT]:
                self.turning_left = True
            if keys[pygame.K_RIGHT]:
                self.turning_right = True
            if keys[pygame.K_SPACE]: # Player 1 fire key
                bullet = self.fire_cannon()
        elif player_num == 2:
            if keys[pygame.K_z]:
                self.accelerating = True
            if keys[pygame.K_s]:
                self.braking = True
            if keys[pygame.K_q]:
                self.turning_left = True
            if keys[pygame.K_d]:
                self.turning_right = True
            if keys[pygame.K_LCTRL]: # Player 2 fire key
                bullet = self.fire_cannon()
        
        return bullet # Return bullet if fired, else None


    def fire_cannon(self):
        """
        Fires a bullet from the car's cannon if available.

        Returns:
            Bullet or None: A new Bullet object if a bullet is fired, otherwise None.
        """
        if self.can_fire and not self.is_disabled and self.bullets_remaining > 0:
            self.can_fire = False
            self.fire_cooldown_timer = self.fire_cooldown
            self.bullets_remaining -= 1  # Décrémente le compteur de balles
            
            # Calculate bullet spawn position
            forward_vector = pygame.math.Vector2(0, -1).rotate(self.angle)
            spawn_offset = forward_vector * (CAR_LENGTH / 2 + BULLET_RADIUS + 5)
            bullet_pos = self.position + spawn_offset
            
            return Bullet(bullet_pos.x, bullet_pos.y, self.angle, self.color)
        return None


    def update_ai(self, target_obj, dt, track_waypoints=None):
        """
        Simple AI logic for the car.

        Args:
            target_obj (pygame.sprite.Sprite): The target to follow or attack.
            dt (float): The time delta since the last frame.
            track_waypoints (list, optional): A list of waypoints for the AI to follow in race mode. Defaults to None.

        Returns:
            Bullet or None: A new Bullet object if the car fires, otherwise None.
        """
        if self.is_disabled: # Ne pas traiter l'IA si la voiture est désactivée
            self.accelerating = self.braking = self.turning_left = self.turning_right = False
            return None # No bullet fired

        self.accelerating = False
        self.braking = False
        self.turning_left = False
        self.turning_right = False
        
        bullet = None

        if self.game_mode == GAME_MODE_RACE and track_waypoints:
            # Race AI logic: follow waypoints
            target_waypoint = pygame.math.Vector2(track_waypoints[self.current_waypoint_index])
            direction_to_target = target_waypoint - self.position
            
            # print(f"AI {self.color} targeting waypoint {self.current_waypoint_index}: {target_waypoint}")
            # print(f"Distance to waypoint: {direction_to_target.length():.2f}")

            # Check if reached current waypoint
            if direction_to_target.length() < CAR_LENGTH * 2: # Increased threshold for reaching waypoint
                self.current_waypoint_index = (self.current_waypoint_index + 1) % len(track_waypoints)
                print(f"AI {self.color} reached waypoint {self.current_waypoint_index - 1}, next: {self.current_waypoint_index}")
                # Update target_waypoint immediately to the new one
                target_waypoint = pygame.math.Vector2(track_waypoints[self.current_waypoint_index])
                direction_to_target = target_waypoint - self.position


            # Always accelerate in race mode
            self.accelerating = True

            # Calculate target angle
            target_angle = math.degrees(math.atan2(-direction_to_target.y, direction_to_target.x))
            target_angle = (90 - target_angle) % 360
            angle_diff = (target_angle - self.angle + 180) % 360 - 180

            # Turn towards target waypoint
            if abs(angle_diff) > 2: # Smaller threshold for turning, more precise
                if angle_diff > 0:
                    self.turning_right = True
                else:
                    self.turning_left = True
            
            # Simple wall avoidance (if too close to a wall, try to turn away)
            # This is a very basic avoidance, a more robust solution would involve raycasting
            # For simplicity, if velocity is low and not facing waypoint, try random turn
            if self.velocity.length() < 50 and abs(angle_diff) > 45:
                if random.random() < 0.5:
                    self.turning_left = True
                else:
                    self.turning_right = True
            
            # AI can also fire in race mode, but let's keep it simple for now (no firing logic for AI in race mode)
            # If you want AI to fire in race mode, add logic here.

        else: # Free Play AI logic (current aggressive behavior)
            if target_obj:
                # If target is a Car, check if it's alive
                if isinstance(target_obj, Car) and target_obj.hp <= 0:
                    return None # Don't target destroyed cars

                direction_to_target = target_obj.position - self.position
                
                # Calculate target angle so it's available for both movement and firing logic
                target_angle = math.degrees(math.atan2(-direction_to_target.y, direction_to_target.x))
                target_angle = (90 - target_angle) % 360
                angle_diff = (target_angle - self.angle + 180) % 360 - 180

                # If the target is very close, just try to ram it
                if direction_to_target.length() < CAR_LENGTH * 2: # Within 2 car lengths
                    self.accelerating = True
                    # No braking here, just ram
                else:
                    # Turn towards target
                    if abs(angle_diff) > 2: # Smaller threshold for turning, more precise
                        if angle_diff > 0:
                            self.turning_right = True
                        else:
                            self.turning_left = True
                    
                    # Accelerate if generally facing the target (wider angle)
                    if abs(angle_diff) < 60: # Accelerate if target is within +/- 60 degrees
                        self.accelerating = True
                    
                    # If AI is stuck or moving very slowly, try to accelerate and turn randomly to get unstuck
                    if self.velocity.length() < 10 and not self.accelerating: # If almost stopped and not trying to accelerate
                        self.accelerating = True
                        if random.random() < 0.5: # Random turn to try and get unstuck
                            self.turning_left = True
                        else:
                            self.turning_right = True
                
                # AI Firing Logic (only in Free Play, targeting other cars)
                if isinstance(target_obj, Car) and self.can_fire and direction_to_target.length() < 300 and abs(angle_diff) < 10:
                    # Fire if target is a car, within range, and mostly in front
                    bullet = self.fire_cannon()

            else: # If no target (e.g., all players disabled), try to move forward a bit
                self.accelerating = True
                # Maybe add some random turning if no target to explore
                if random.random() < 0.01: # Small chance to turn
                    if random.random() < 0.5:
                        self.turning_left = True
                    else:
                        self.turning_right = True
        
        return bullet # Return bullet if AI fired, else None


    def apply_forces(self, dt):
        """
        Calculates and applies linear and angular forces to the car.

        Args:
            dt (float): The time delta since the last frame.
        """
        forward_vector = pygame.math.Vector2(0, -1).rotate(self.angle)

        engine_force = pygame.math.Vector2(0, 0)
        if self.accelerating:
            engine_force = forward_vector * ENGINE_FORCE * self.speed_multiplier # Apply speed multiplier for AI
        elif self.braking:
            if self.velocity.length() > 0:
                engine_force = -self.velocity.normalize() * BRAKE_FORCE * self.speed_multiplier # Apply speed multiplier for AI

        friction_force = -self.velocity * FRICTION_COEFF * self.mass
        drag_force = pygame.math.Vector2(0,0)
        if self.velocity.length() > 0:
            drag_force = -self.velocity.normalize() * DRAG_COEFF * self.velocity.length_squared()

        total_linear_force = engine_force + friction_force + drag_force
        acceleration = total_linear_force / self.mass

        self.velocity += acceleration * dt

        angular_acceleration = 0
        if self.turning_left:
            angular_acceleration = -ANGULAR_ACCELERATION_MAGNITUDE / self.inertia
        if self.turning_right:
            angular_acceleration = ANGULAR_ACCELERATION_MAGNITUDE / self.inertia

        angular_friction = -self.angular_velocity * 0.9
        angular_acceleration += angular_friction

        self.angular_velocity += angular_acceleration * dt
        self.angular_velocity *= 0.95

    def update_physics(self, dt):
        """
        Updates the car's position and angle based on physics.

        Args:
            dt (float): The time delta since the last frame.
        """
        # Update cannon cooldown
        if not self.can_fire:
            self.fire_cooldown_timer -= dt
            if self.fire_cooldown_timer <= 0:
                self.can_fire = True

        if self.hp <= 0 and not self.is_disabled: # Si HP <=0 et pas encore désactivée, on la désactive
            self.is_disabled = True
            self.disabled_timer = DISABLED_DURATION
            self.velocity = pygame.math.Vector2(0,0) # Arrêter la voiture
            self.angular_velocity = 0
            # if self.engine_sound: # REMOVED
            #     self.engine_sound.stop() # REMOVED
            print(f"Voiture {self.color} est désactivée pour {DISABLED_DURATION} secondes.")

        if self.is_disabled: # Gérer le timer de désactivation
            self.disabled_timer -= dt
            if self.disabled_timer <= 0:
                self.hp = MAX_HP # Réinitialiser les PV
                self.is_disabled = False
                self.position = self.initial_position # Revenir à la position initiale
                self.angle = self.initial_angle
                self.velocity = pygame.math.Vector2(0,0)
                self.angular_velocity = 0
                # if self.engine_sound and self.is_player: # REMOVED
                #     self.engine_sound.play(-1) # REMOVED
                print(f"Voiture {self.color} est réactivée.")
            return # Ne pas appliquer la physique si désactivée

        self.apply_forces(dt)

        self.position += self.velocity * dt
        self.angle += self.angular_velocity * dt
        self.angle %= 360

        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

        for i, point in enumerate(self.base_points):
            self.rotated_points[i] = point.rotate(self.angle) + self.position


    def get_collision_polygon(self):
        """
        Returns the vertices of the car's collision polygon in world coordinates.

        Returns:
            list: A list of pygame.math.Vector2 objects representing the polygon's vertices.
        """
        return self.rotated_points

    def get_zone_from_impact_point(self, impact_point_world):
        """
        Determines the most likely impact zone based on the impact point.

        Args:
            impact_point_world (pygame.math.Vector2): The impact point in world coordinates.

        Returns:
            str: The name of the impact zone ("front", "sides", or "rear").
        """
        distances = []
        for i, p in enumerate(self.rotated_points):
            distances.append((i, (impact_point_world - p).length()))
        
        distances.sort(key=lambda x: x[1])
        closest_point_index = distances[0][0]

        if closest_point_index == 0:
            return "front"
        elif closest_point_index == 1 or closest_point_index == 2:
            return "sides"

        return "sides"


    def take_damage(self, impact_force, impact_point_world, attacker=None):
        """
        Calculates and applies damage to the car.

        Args:
            impact_force (float): The magnitude of the impact force.
            impact_point_world (pygame.math.Vector2): The point of contact in world coordinates.
            attacker (Car, optional): The car that inflicted the damage. Defaults to None.
        """
        if self.hp <= 0: # Si déjà détruite, ne prend pas plus de dégâts
            return

        if impact_force < MIN_IMPACT_FORCE_FOR_DAMAGE:
            return

        impact_zone_key = self.get_zone_from_impact_point(impact_point_world)
        zone_resistance = self.damage_zones.get(impact_zone_key, {"resistance": 1.0})["resistance"]

        damage = (impact_force * DAMAGE_FACTOR) / zone_resistance

        self.hp -= damage
        print(f"Voiture {self.color} a subi {damage:.2f} dégâts sur la zone '{impact_zone_key}'. HP restants: {self.hp:.2f}")

        if self.hp <= 0: # Si les PV tombent à 0
            self.hp = 0 # S'assurer que les PV ne sont pas négatifs
            if attacker and attacker != self: # Si un attaquant est spécifié et n'est pas soi-même
                attacker.score += SCORE_INCREMENT
                print(f"Voiture {attacker.color} marque un point ! Score: {attacker.score}")
            print(f"La voiture {self.color} est détruite !")
            # La voiture n'est pas tuée ici, mais désactivée par update_physics
            # self.kill() # Retire le sprite de tous les groupes (si on voulait la retirer définitivement)

        if self.collision_sound:
            self.collision_sound.play()

    def heal(self, amount):
        """
        Heals the car by a certain amount of HP.

        Args:
            amount (int): The amount of HP to heal.
        """
        if self.hp <= 0: # Ne pas soigner une voiture désactivée
            return
        old_hp = self.hp
        self.hp = min(MAX_HP, self.hp + amount)
        print(f"Voiture {self.color} a récupéré {self.hp - old_hp:.2f} PV. HP actuels: {self.hp:.2f}")
        if self.pickup_sound:
            self.pickup_sound.play()


    def draw(self, screen):
        """
        Draws the car on the screen.

        Args:
            screen (pygame.Surface): The screen to draw the car on.
        """
        if self.hp <= 0 and not self.is_disabled: # Ne pas dessiner si détruite et pas en phase de désactivation
            return
        
        # Rendre la voiture semi-transparente si désactivée
        if self.is_disabled:
            temp_image = self.image.copy()
            temp_image.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT) # Applique une transparence
            screen.blit(temp_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

        # Dessiner la barre de vie (même si désactivée pour montrer le timer ou l'état)
        hp_bar_width = CAR_WIDTH
        hp_bar_height = 5
        hp_ratio = self.hp / MAX_HP
        hp_bar_color = GREEN if hp_ratio > 0.5 else ORANGE if hp_ratio > 0.2 else RED
        
        hp_bar_x = self.rect.centerx - hp_bar_width / 2
        hp_bar_y = self.rect.centery + CAR_LENGTH / 2 + 5
        
        pygame.draw.rect(screen, hp_bar_color, (hp_bar_x, hp_bar_y, hp_bar_width * hp_ratio, hp_bar_height))
        pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 1)

        # Afficher le timer de désactivation si la voiture est désactivée
        if self.is_disabled:
            font_timer = pygame.font.Font(None, 24)
            timer_text = font_timer.render(f"{self.disabled_timer:.1f}s", True, WHITE)
            screen.blit(timer_text, timer_text.get_rect(center=(self.rect.centerx, self.rect.top - 15)))


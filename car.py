import pygame
import math
import random
from constants import * # Import all constants
from collision_utils import resolve_collision # Import collision resolution function

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, color=BLUE, is_player=True):
        super().__init__()
        # --- NOUVEAU MESSAGE DE DÉBOGAGE ---
        print(f"Creating Car: Color={color}, Player={is_player}, Initial Pos=({x}, {y})")
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

        # Flags de contrôle
        self.accelerating = False
        self.braking = False
        self.turning_left = False
        self.turning_right = False

        # État de désactivation après destruction
        self.is_disabled = False
        self.disabled_timer = 0.0

        # Points de la forme de la "part de pizza" (relatifs au centre de la voiture)
        self.base_points = [
            pygame.math.Vector2(0, -CAR_LENGTH / 2),  # Pointe avant (index 0)
            pygame.math.Vector2(-CAR_WIDTH / 2, CAR_LENGTH / 2), # Bas-gauche (index 1)
            pygame.math.Vector2(CAR_WIDTH / 2, CAR_LENGTH / 2)   # Bas-droite (index 2)
        ]
        self.rotated_points = [pygame.math.Vector2(0,0), pygame.math.Vector2(0,0), pygame.math.Vector2(0,0)] # Points after rotation

        # Zones de dégâts avec résistances
        self.damage_zones = {
            "front": {"resistance": 1.5},
            "sides": {"resistance": 0.8},
            "rear": {"resistance": 1.0}
        }

        # Sons
        self.engine_sound = None
        self.collision_sound = None
        self.pickup_sound = None
        try:
            self.engine_sound = pygame.mixer.Sound(SOUND_ENGINE_PATH)
            self.engine_sound.set_volume(0.3)
            if self.is_player:
                self.engine_sound.play(-1)
        except pygame.error as e:
            print(f"Error loading engine sound: {e}")
        
        try:
            self.collision_sound = pygame.mixer.Sound(SOUND_COLLISION_PATH)
            self.collision_sound.set_volume(0.5)
        except pygame.error as e:
            print(f"Error loading collision sound: {e}")

        try:
            self.pickup_sound = pygame.mixer.Sound(SOUND_PICKUP_PATH)
            self.pickup_sound.set_volume(0.6)
        except pygame.error as e:
            print(f"Error loading pickup sound: {e}")


    def create_pizza_slice_surface(self, width, length, color):
        """Creates a Pygame surface with a pizza slice shape."""
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
        """Handles keyboard inputs to control the car."""
        if self.is_disabled: # Do not process inputs if car is disabled
            self.accelerating = self.braking = self.turning_left = self.turning_right = False
            return

        self.accelerating = False
        self.braking = False
        self.turning_left = False
        self.turning_right = False

        if player_num == 1:
            if keys[pygame.K_UP]:
                self.accelerating = True
            if keys[pygame.K_DOWN]:
                self.braking = True
            if keys[pygame.K_LEFT]:
                self.turning_left = True
            if keys[pygame.K_RIGHT]:
                self.turning_right = True
        elif player_num == 2:
            if keys[pygame.K_z]:
                self.accelerating = True
            if keys[pygame.K_s]:
                self.braking = True
            if keys[pygame.K_q]:
                self.turning_left = True
            if keys[pygame.K_d]:
                self.turning_right = True

    def update_ai(self, target_obj, dt):
        """Simple AI logic for the car."""
        if self.is_disabled: # Do not process AI if car is disabled
            self.accelerating = self.braking = self.turning_left = self.turning_right = False
            return

        self.accelerating = False
        self.braking = False
        self.turning_left = False
        self.turning_right = False

        if target_obj:
            # If target is a Car, check if it's alive
            if isinstance(target_obj, Car) and target_obj.hp <= 0:
                return # Don't target destroyed cars

            direction_to_target = target_obj.position - self.position
            
            # If the target is very close, just try to ram it
            if direction_to_target.length() < CAR_LENGTH * 2: # Within 2 car lengths
                self.accelerating = True
                # No braking here, just ram
            else:
                # Calculate target angle
                target_angle = math.degrees(math.atan2(-direction_to_target.y, direction_to_target.x))
                target_angle = (90 - target_angle) % 360
                angle_diff = (target_angle - self.angle + 180) % 360 - 180

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
        else: # If no target, try to move forward a bit
            self.accelerating = True
            # Maybe add some random turning if no target to explore
            if random.random() < 0.01: # Small chance to turn
                if random.random() < 0.5:
                    self.turning_left = True
                else:
                    self.turning_right = True


    def apply_forces(self, dt):
        """Calculates and applies linear forces and angular torques."""
        forward_vector = pygame.math.Vector2(0, -1).rotate(self.angle)

        engine_force = pygame.math.Vector2(0, 0)
        if self.accelerating:
            engine_force = forward_vector * ENGINE_FORCE
        elif self.braking:
            if self.velocity.length() > 0:
                engine_force = -self.velocity.normalize() * BRAKE_FORCE

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
        """Updates car position and angle based on physics."""
        if self.hp <= 0 and not self.is_disabled: # If HP <=0 and not yet disabled, disable it
            self.is_disabled = True
            self.disabled_timer = DISABLED_DURATION
            self.velocity = pygame.math.Vector2(0,0) # Stop the car
            self.angular_velocity = 0
            if self.engine_sound:
                self.engine_sound.stop()
            print(f"Voiture {self.color} est désactivée pour {DISABLED_DURATION} secondes.")

        if self.is_disabled: # Manage disabled timer
            self.disabled_timer -= dt
            if self.disabled_timer <= 0:
                self.hp = MAX_HP # Reset HP
                self.is_disabled = False
                self.position = self.initial_position # Return to initial position
                self.angle = self.initial_angle
                self.velocity = pygame.math.Vector2(0,0)
                self.angular_velocity = 0
                if self.engine_sound and self.is_player: # Restart sound if it's a player
                    self.engine_sound.play(-1)
                print(f"Voiture {self.color} est réactivée.")
            return # Do not apply physics if disabled

        self.apply_forces(dt)

        self.position += self.velocity * dt
        self.angle += self.angular_velocity * dt
        self.angle %= 360

        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

        for i, point in enumerate(self.base_points):
            self.rotated_points[i] = point.rotate(self.angle) + self.position

        # NOUVEAU: Limiter la voiture à l'écran et infliger des dégâts si collision avec les bords
        collided_with_screen_edge = False
        if self.position.x < 0:
            self.position.x = 0
            self.velocity.x *= -COLLISION_ELASTICITY
            collided_with_screen_edge = True
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH
            self.velocity.x *= -COLLISION_ELASTICITY
            collided_with_screen_edge = True
            
        if self.position.y < 0:
            self.position.y = 0
            self.velocity.y *= -COLLISION_ELASTICITY
            collided_with_screen_edge = True
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = SCREEN_HEIGHT
            self.velocity.y *= -COLLISION_ELASTICITY
            collided_with_screen_edge = True

        if collided_with_screen_edge:
            # Appliquer des dégâts si la voiture touche un bord de l'écran
            self.take_damage(WALL_DAMAGE_FACTOR, self.position)


    def get_collision_polygon(self):
        """Returns the vertices of the car's collision polygon in world coordinates."""
        return self.rotated_points

    def get_zone_from_impact_point(self, impact_point_world):
        """
        Determines the most likely impact zone based on the impact point.
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
        impact_force: The magnitude of the impact force.
        impact_point_world: The contact point in world coordinates.
        attacker: The car that inflicted damage (None for walls).
        """
        if self.hp <= 0: # If already destroyed, do not take more damage
            return

        if impact_force < MIN_IMPACT_FORCE_FOR_DAMAGE:
            return

        impact_zone_key = self.get_zone_from_impact_point(impact_point_world)
        zone_resistance = self.damage_zones.get(impact_zone_key, {"resistance": 1.0})["resistance"]

        damage = (impact_force * DAMAGE_FACTOR) / zone_resistance

        self.hp -= damage
        print(f"Voiture {self.color} a subi {damage:.2f} dégâts sur la zone '{impact_zone_key}'. HP restants: {self.hp:.2f}")

        if self.hp <= 0: # If HP drops to 0
            self.hp = 0 # Ensure HP is not negative
            if attacker and attacker != self: # If an attacker is specified and is not self
                attacker.score += SCORE_INCREMENT
                print(f"Voiture {attacker.color} marque un point ! Score: {attacker.score}")
            print(f"La voiture {self.color} est détruite !")
            # La voiture n'est pas tuée ici, mais désactivée par update_physics
            # self.kill() # Retire le sprite de tous les groupes (si on voulait la retirer définitivement)

        if self.collision_sound:
            self.collision_sound.play()

    def heal(self, amount):
        """Soigne la voiture d'un certain montant de PV."""
        if self.hp <= 0: # Ne pas soigner une voiture désactivée
            return
        old_hp = self.hp
        self.hp = min(MAX_HP, self.hp + amount)
        print(f"Voiture {self.color} a récupéré {self.hp - old_hp:.2f} PV. HP actuels: {self.hp:.2f}")
        if self.pickup_sound:
            self.pickup_sound.play()


    def draw(self, screen):
        """Dessine la voiture sur l'écran."""
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

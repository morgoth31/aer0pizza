import pygame
import math
import random

# --- Constantes du Jeu ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 900
FPS = 60
GAME_TITLE = "Jeu de Voiture 2D - Prototype Amélioré 4"

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50) # Couleur pour la piste
WALL_COLOR = (70, 70, 70) # Couleur des murs de la piste

# --- Paramètres de la Voiture ---
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

# --- Paramètres de Collision ---
COLLISION_ELASTICITY = 0.7 # Coefficient de restitution (0 = pas de rebond, 1 = rebond parfait)
COLLISION_FRICTION = 0.5 # Coefficient de frottement lors de la collision
DAMAGE_FACTOR = 0.03 # Facteur de base pour calibrer les dégâts (ajuster selon les tests)
COLLISION_DAMAGE_MULTIPLIER = 5.0 # Multiplicateur de dégâts pour les impacts entre voitures
WALL_DAMAGE_FACTOR = 500.0 # Dégâts subis lors de la collision avec les bords
MIN_IMPACT_FORCE_FOR_DAMAGE = 0.0001 # Seuil minimum de force d'impact pour infliger des dégâts
FRONT_IMPACT_THRESHOLD = 0.7 # Seuil du produit scalaire pour déterminer un impact "de face"

# --- Paramètres de Jeu ---
DISABLED_DURATION = 3.0 # Durée en secondes pendant laquelle une voiture est désactivée après destruction
SCORE_INCREMENT = 1 # Points gagnés lorsqu'une voiture est détruite
HEALTH_PICKUP_SPAWN_INTERVAL = 10.0 # Fréquence d'apparition des bonus de vie en secondes
HEALTH_PICKUP_MIN_HP = 5 # Points de vie minimum récupérés par un bonus
HEALTH_PICKUP_MAX_HP = 15 # Points de vie maximum récupérés par un bonus
HEALTH_PICKUP_RADIUS = 15 # Rayon du cercle du bonus de vie


# --- Sons ---
# Chemin des fichiers sonores (à adapter par l'utilisateur)
# Assurez-vous d'avoir ces fichiers .mp3 dans le même répertoire que le script
SOUND_ENGINE_PATH = "assets/engine_loop.mp3" # Son de moteur en boucle
SOUND_COLLISION_PATH = "assets/collision.mp3" # Son de collision
SOUND_MENU_SELECT_PATH = "assets/menu_select.mp3" # Son de sélection de menu
SOUND_PICKUP_PATH = "assets/pickup.mp3" # Son de ramassage de bonus de vie


# --- Classe Car ---
class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, color=BLUE, is_player=True):
        super().__init__()
        self.original_image = self.create_pizza_slice_surface(CAR_WIDTH, CAR_LENGTH, color)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.initial_position = pygame.math.Vector2(x, y) # Pour le respawn
        self.initial_angle = angle # Pour le respawn

        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = angle  # Angle en degrés (0 = vers le haut, 90 = vers la droite)
        self.angular_velocity = 0 # Vitesse angulaire en degrés par seconde

        self.mass = CAR_MASS
        self.inertia = CAR_INERTIA
        self.hp = MAX_HP
        self.is_player = is_player # True si contrôlé par le joueur, False si IA
        self.score = 0 # Score de la voiture

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
        self.rotated_points = [pygame.math.Vector2(0,0), pygame.math.Vector2(0,0), pygame.math.Vector2(0,0)] # Points après rotation

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


    def create_pizza_slice_surface(self, width, length, color):
        """Crée une surface Pygame avec la forme d'une part de pizza."""
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
        """Gère les inputs clavier pour contrôler la voiture."""
        if self.is_disabled: # Ne pas traiter les inputs si la voiture est désactivée
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

    def update_ai(self, target_car, dt):
        """Logique d'IA simple pour la voiture."""
        if self.is_disabled: # Ne pas traiter l'IA si la voiture est désactivée
            self.accelerating = self.braking = self.turning_left = self.turning_right = False
            return

        self.accelerating = False
        self.braking = False
        self.turning_left = False
        self.turning_right = False

        if target_car and target_car.hp > 0: # Cible uniquement si la voiture est vivante
            direction_to_target = target_car.position - self.position
            target_angle = math.degrees(math.atan2(-direction_to_target.y, direction_to_target.x))
            
            target_angle = (90 - target_angle) % 360

            angle_diff = (target_angle - self.angle + 180) % 360 - 180

            if abs(angle_diff) > 5:
                if angle_diff > 0:
                    self.turning_right = True
                else:
                    self.turning_left = True
            
            if direction_to_target.length() > 100 and abs(angle_diff) < 45:
                self.accelerating = True
            
            if direction_to_target.length() < 150 and self.velocity.length() > 50:
                self.braking = True
            
            if self.velocity.length() < 10 and not self.accelerating and not self.braking:
                self.accelerating = True
                if random.random() < 0.5:
                    self.turning_left = True
                else:
                    self.turning_right = True


    def apply_forces(self, dt):
        """Calcule et applique les forces linéaires et les couples angulaires."""
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
        """Met à jour la position et l'angle de la voiture en fonction de la physique."""
        if self.hp <= 0 and not self.is_disabled: # Si HP <=0 et pas encore désactivée, on la désactive
            self.is_disabled = True
            self.disabled_timer = DISABLED_DURATION
            self.velocity = pygame.math.Vector2(0,0) # Arrêter la voiture
            self.angular_velocity = 0
            if self.engine_sound:
                self.engine_sound.stop()
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
                if self.engine_sound and self.is_player: # Redémarrer le son si c'est un joueur
                    self.engine_sound.play(-1)
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

        # La logique de collision avec les bords de l'écran est maintenant gérée par les murs de la piste.
        # Cette section est commentée car elle serait redondante avec les murs.
        # collided_with_wall = False
        # if self.position.x < 0:
        #     self.position.x = 0
        #     self.velocity.x *= -COLLISION_ELASTICITY
        #     collided_with_wall = True
        # elif self.position.x > SCREEN_WIDTH:
        #     self.position.x = SCREEN_WIDTH
        #     self.velocity.x *= -COLLISION_ELASTICITY
        #     collided_with_wall = True
            
        # if self.position.y < 0:
        #     self.position.y = 0
        #     self.velocity.y *= -COLLISION_ELASTICITY
        #     collided_with_wall = True
        # elif self.position.y > SCREEN_HEIGHT:
        #     self.position.y = SCREEN_HEIGHT
        #     self.velocity.y *= -COLLISION_ELASTICITY
        #     collided_with_wall = True

        # if collided_with_wall:
        #     self.take_damage(WALL_DAMAGE_FACTOR, self.position)


    def get_collision_polygon(self):
        """Retourne les sommets du polygone de collision de la voiture en coordonnées monde."""
        return self.rotated_points

    def get_zone_from_impact_point(self, impact_point_world):
        """
        Détermine la zone d'impact la plus probable basée sur le point d'impact.
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
        Calcule et applique les dégâts à la voiture.
        impact_force: La magnitude de la force d'impact.
        impact_point_world: Le point de contact en coordonnées monde.
        attacker: La voiture qui a infligé les dégâts (None pour les murs).
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


# --- Classe HealthPickup ---
class HealthPickup(pygame.sprite.Sprite):
    def __init__(self, x, y, hp_value):
        super().__init__()
        self.position = pygame.math.Vector2(x, y)
        self.hp_value = hp_value
        self.radius = HEALTH_PICKUP_RADIUS
        self.color = GREEN # Couleur du bonus de vie
        self.font = pygame.font.Font(None, 20)
        self.text_surface = self.font.render(f"+{hp_value}", True, WHITE)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        """Dessine le bonus de vie."""
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.position.x), int(self.position.y)), self.radius, 1) # Contour
        screen.blit(self.text_surface, self.text_surface.get_rect(center=(int(self.position.x), int(self.position.y))))

# --- Classe Wall ---
class Wall(pygame.sprite.Sprite):
    def __init__(self, p1, p2, thickness=10, color=WALL_COLOR):
        super().__init__()
        self.p1 = pygame.math.Vector2(p1)
        self.p2 = pygame.math.Vector2(p2)
        self.thickness = thickness
        self.color = color

        # Calculer la normale du mur (pointant vers l'extérieur de la piste)
        # Pour un segment (p1, p2), le vecteur est (p2-p1).
        # La normale est (-dy, dx) ou (dy, -dx).
        # Il faut s'assurer qu'elle pointe vers l'extérieur.
        edge = self.p2 - self.p1
        self.normal = pygame.math.Vector2(-edge.y, edge.x).normalize()
        
        # Pour un mur simple, le "polygone" est un rectangle épais.
        # On peut aussi le traiter comme un segment pour le SAT avec un polygone.
        # Pour une détection plus robuste, on peut considérer le mur comme un rectangle.
        # Ici, nous allons simplifier en utilisant le segment et sa normale.
        
        # Calculer un rect englobant pour le dessin et une première approximation de collision
        min_x = min(self.p1.x, self.p2.x) - thickness / 2
        max_x = max(self.p1.x, self.p2.x) + thickness / 2
        min_y = min(self.p1.y, self.p2.y) - thickness / 2
        max_y = max(self.p1.y, self.p2.y) + thickness / 2
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def get_collision_line_segment(self):
        """Retourne le segment de ligne et sa normale pour la collision."""
        return self.p1, self.p2, self.normal

    def draw(self, screen):
        """Dessine le mur."""
        pygame.draw.line(screen, self.color, self.p1, self.p2, self.thickness)


# --- Fonctions Utilitaires pour les Collisions (SAT et Impulsion) ---

def project_polygon(axis, polygon_points):
    """Projete un polygone sur un axe et retourne l'intervalle [min, max]."""
    min_proj = float('inf')
    max_proj = float('-inf')
    for p in polygon_points:
        proj = p.dot(axis)
        min_proj = min(min_proj, proj)
        max_proj = max(max_proj, proj)
    return min_proj, max_proj

def get_axes(polygon_points):
    """Retourne les axes normaux à chaque arête d'un polygone."""
    axes = []
    for i in range(len(polygon_points)):
        p1 = polygon_points[i]
        p2 = polygon_points[(i + 1) % len(polygon_points)]
        edge = p2 - p1
        axis = pygame.math.Vector2(-edge.y, edge.x).normalize()
        axes.append(axis)
    return axes

def collide_polygons_sat(poly1_points, poly2_points):
    """
    Détecte la collision entre deux polygones convexes en utilisant le SAT.
    Retourne (True, normal, penetration) si collision, sinon (False, None, None).
    """
    axes = get_axes(poly1_points) + get_axes(poly2_points)
    
    min_overlap = float('inf')
    collision_normal = None

    for axis in axes:
        proj1_min, proj1_max = project_polygon(axis, poly1_points)
        proj2_min, proj2_max = project_polygon(axis, poly2_points)

        overlap = max(0, min(proj1_max, proj2_max) - max(proj1_min, proj2_min))

        if overlap == 0:
            return False, None, None
        
        if overlap < min_overlap:
            min_overlap = overlap
            collision_normal = axis

    center1 = sum(poly1_points, pygame.math.Vector2(0,0)) / len(poly1_points)
    center2 = sum(poly2_points, pygame.math.Vector2(0,0)) / len(poly2_points)
    
    direction = center2 - center1
    if collision_normal.dot(direction) < 0:
        collision_normal *= -1

    return True, collision_normal, min_overlap

def collide_car_wall_sat(car, wall):
    """
    Détecte la collision entre une voiture (polygone) et un mur (segment de ligne).
    Retourne (True, normal, penetration) si collision, sinon (False, None, None).
    """
    car_points = car.get_collision_polygon()
    wall_p1, wall_p2, wall_normal = wall.get_collision_line_segment()

    # Les axes pour le SAT sont les normales des arêtes de la voiture
    # et la normale du mur (et potentiellement l'arête du mur elle-même, mais pour un segment,
    # seule la normale du segment est un axe de séparation).
    axes = get_axes(car_points) + [wall_normal]

    min_overlap = float('inf')
    collision_normal = None

    for axis in axes:
        proj_car_min, proj_car_max = project_polygon(axis, car_points)
        proj_wall_min = wall_p1.dot(axis)
        proj_wall_max = wall_p2.dot(axis)
        
        # Pour un segment, l'intervalle est juste entre ses deux points projetés
        if proj_wall_min > proj_wall_max: # S'assurer que min est bien min
            proj_wall_min, proj_wall_max = proj_wall_max, proj_wall_min

        overlap = max(0, min(proj_car_max, proj_wall_max) - max(proj_car_min, proj_wall_min))

        if overlap == 0:
            return False, None, None
        
        if overlap < min_overlap:
            min_overlap = overlap
            collision_normal = axis

    # S'assurer que la normale pointe de la voiture vers le mur
    car_center = sum(car_points, pygame.math.Vector2(0,0)) / len(car_points)
    # Point milieu du mur
    wall_center = (wall_p1 + wall_p2) / 2
    
    direction = wall_center - car_center
    if collision_normal.dot(direction) < 0:
        collision_normal *= -1

    return True, collision_normal, min_overlap


def resolve_collision(obj1, obj2, normal, penetration):
    """
    Résout une collision entre deux objets (voiture-voiture ou voiture-mur).
    obj1: Le premier objet (toujours une voiture pour l'instant).
    obj2: Le deuxième objet (voiture ou mur).
    normal: La normale de collision (vecteur unitaire).
    penetration: La profondeur de pénétration.
    """
    # 1. Séparer les objets (résoudre la pénétration)
    # Pour voiture-voiture, on distribue le déplacement. Pour voiture-mur, seule la voiture bouge.
    if isinstance(obj2, Car): # Collision voiture-voiture
        total_inv_mass = (1 / obj1.mass) + (1 / obj2.mass)
        if total_inv_mass == 0: return

        resolution_vector = normal * penetration / total_inv_mass
        obj1.position -= resolution_vector / obj1.mass
        obj2.position += resolution_vector / obj2.mass
    else: # Collision voiture-mur (obj2 est un Wall)
        obj1.position -= normal * penetration

    # Mettre à jour les rects et points des voitures après la résolution de la pénétration
    obj1.update_physics(0)
    if isinstance(obj2, Car):
        obj2.update_physics(0)

    # 2. Calculer l'impulsion (seulement pour les voitures)
    if isinstance(obj2, Car): # Collision voiture-voiture
        relative_velocity = obj2.velocity - obj1.velocity
    else: # Collision voiture-mur
        relative_velocity = -obj1.velocity # La vitesse relative est juste l'opposé de la vitesse de la voiture

    vel_along_normal = relative_velocity.dot(normal)

    if vel_along_normal > 0: # Si les objets s'éloignent déjà
        return

    e = COLLISION_ELASTICITY

    # Calcul de l'impulsion scalaire
    if isinstance(obj2, Car):
        j = -(1 + e) * vel_along_normal
        j /= total_inv_mass
    else: # Collision voiture-mur (masse infinie pour le mur)
        j = -(1 + e) * vel_along_normal * obj1.mass # J = -(1+e) * v_rel_n * m

    impulse = normal * j
    obj1.velocity -= impulse / obj1.mass
    if isinstance(obj2, Car):
        obj2.velocity += impulse / obj2.mass

    # 3. Résolution du frottement (simple)
    tangent = relative_velocity - (vel_along_normal * normal)
    if tangent.length() > 0:
        tangent = tangent.normalize()

    sf = COLLISION_FRICTION

    jt = -relative_velocity.dot(tangent)
    if isinstance(obj2, Car):
        jt /= total_inv_mass
    else: # Collision voiture-mur
        jt *= obj1.mass # Jt = -v_rel_t * m

    if abs(jt) > j * sf:
        jt = j * sf * (-1 if jt < 0 else 1)

    friction_impulse = tangent * jt
    obj1.velocity -= friction_impulse / obj1.mass
    if isinstance(obj2, Car):
        obj2.velocity += friction_impulse / obj2.mass

    # 4. Calcul des dégâts
    impact_force = (j / pygame.time.get_ticks() * 1000) # Approximation de F = dp/dt

    if isinstance(obj2, Car): # Dégâts voiture-voiture
        impact_force *= COLLISION_DAMAGE_MULTIPLIER
        impact_point = (obj1.position + obj2.position) / 2

        car_a_forward = pygame.math.Vector2(0, -1).rotate(obj1.angle)
        dot_prod_a_normal = car_a_forward.dot(normal)

        car_b_forward = pygame.math.Vector2(0, -1).rotate(obj2.angle)
        dot_prod_b_neg_normal = car_b_forward.dot(-normal)

        car_a_inflicts_damage = dot_prod_a_normal > FRONT_IMPACT_THRESHOLD
        car_b_inflicts_damage = dot_prod_b_neg_normal > FRONT_IMPACT_THRESHOLD

        if car_a_inflicts_damage:
            obj2.take_damage(impact_force, impact_point, attacker=obj1)
        if car_b_inflicts_damage:
            obj1.take_damage(impact_force, impact_point, attacker=obj2)
    else: # Dégâts voiture-mur
        obj1.take_damage(WALL_DAMAGE_FACTOR, obj1.position) # Le point d'impact est approximé par la position de la voiture


# --- Fonction pour le Menu de Démarrage ---
def main_menu(screen):
    font_title = pygame.font.Font(None, 74)
    font_options = pygame.font.Font(None, 48)
    
    title_text = font_title.render(GAME_TITLE, True, WHITE)
    start_text = font_options.render("Appuyez sur ENTRER pour commencer", True, WHITE)
    controls_text_p1 = font_options.render("Joueur 1 (Bleu): Flèches directionnelles", True, WHITE)
    
    option_player2 = font_options.render("Joueur 2: JOUER (Z/Q/S/D)", True, YELLOW)
    option_ai = font_options.render("Joueur 2: IA", True, WHITE)

    selected_option = 0 # 0 for Player 2, 1 for AI

    menu_select_sound = None
    try:
        menu_select_sound = pygame.mixer.Sound(SOUND_MENU_SELECT_PATH)
        menu_select_sound.set_volume(0.7)
    except pygame.error as e:
        print(f"Erreur de chargement du son du menu: {e}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.K_F11: # Toggle Fullscreen
                pygame.display.toggle_fullscreen()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if menu_select_sound: menu_select_sound.play()
                    return selected_option == 1 # True if AI selected, False if Player 2 selected
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected_option = 1 - selected_option # Toggle between 0 and 1
                    if menu_select_sound: menu_select_sound.play()
        
        # Update option colors
        if selected_option == 0:
            option_player2 = font_options.render("Joueur 2: JOUER (Z/Q/S/D)", True, YELLOW)
            option_ai = font_options.render("Joueur 2: IA", True, WHITE)
        else:
            option_player2 = font_options.render("Joueur 2: JOUER (Z/Q/S/D)", True, WHITE)
            option_ai = font_options.render("Joueur 2: IA", True, YELLOW)

        screen.fill(BLACK)
        
        # Centrer les textes
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)))
        screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)))
        screen.blit(controls_text_p1, controls_text_p1.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)))
        
        screen.blit(option_player2, option_player2.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 0)))
        screen.blit(option_ai, option_ai.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)))

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

# --- Fonction principale du jeu ---
def game_loop():
    pygame.init()
    pygame.mixer.init()

    # Initialisation de l'écran en mode fenêtré par défaut
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

    car2_is_ai = main_menu(screen)

    # Définition de la piste (un simple rectangle pour commencer)
    # Les points sont définis dans le sens horaire pour que les normales pointent vers l'intérieur
    # Pour que la normale pointe vers l'extérieur, il faut définir les points dans le sens anti-horaire
    # ou inverser la normale après calcul. J'ai choisi de définir la normale dans Wall.
    track_walls_points = [
        # Mur extérieur
        (50, 50), (SCREEN_WIDTH - 50, 50), # Top
        (SCREEN_WIDTH - 50, 50), (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50), # Right
        (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50), (50, SCREEN_HEIGHT - 50), # Bottom
        (50, SCREEN_HEIGHT - 50), (50, 50), # Left
        # Mur intérieur (pour faire une piste)
        (150, 150), (150, SCREEN_HEIGHT - 150), # Left Inner
        (150, SCREEN_HEIGHT - 150), (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150), # Bottom Inner
        (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150), (SCREEN_WIDTH - 150, 150), # Right Inner
        (SCREEN_WIDTH - 150, 150), (150, 150) # Top Inner
    ]
    walls = pygame.sprite.Group()
    for i in range(0, len(track_walls_points), 2):
        walls.add(Wall(track_walls_points[i], track_walls_points[i+1]))


    car1 = Car(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, angle=90, color=BLUE, is_player=True)
    car2 = Car(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2, angle=-90, color=RED, is_player=not car2_is_ai)

    all_cars = pygame.sprite.Group(car1, car2)
    health_pickups = pygame.sprite.Group() # Groupe pour les bonus de vie

    health_pickup_spawn_timer = 0.0
    font_score = pygame.font.Font(None, 36)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11: # Toggle Fullscreen
                    pygame.display.toggle_fullscreen()

        keys = pygame.key.get_pressed()
        car1.handle_input(keys, player_num=1)
        
        if not car2_is_ai:
            car2.handle_input(keys, player_num=2)
        else:
            # L'IA de car2 cible car1 si car1 est vivante, sinon elle ne fait rien
            if car1.hp > 0:
                car2.update_ai(car1, dt)
            else: # Si car1 est détruite, l'IA de car2 peut chercher des bonus de vie ou rester immobile
                car2.accelerating = car2.braking = car2.turning_left = car2.turning_right = False
                # Optionnel: IA pourrait cibler le bonus de vie le plus proche
                if health_pickups.sprites():
                    closest_pickup = min(health_pickups.sprites(), key=lambda p: (car2.position - p.position).length())
                    car2.update_ai(closest_pickup, dt) # L'IA cible le bonus de vie

        # --- Mise à jour du jeu ---
        for car in all_cars:
            car.update_physics(dt)

        # Vérification et résolution des collisions entre voitures
        live_cars = [car for car in all_cars if car.hp > 0 or car.is_disabled]
        for i, car_a in enumerate(live_cars):
            for j, car_b in enumerate(live_cars):
                if i < j:
                    if car_a.is_disabled or car_b.is_disabled:
                        continue

                    poly_a = car_a.get_collision_polygon()
                    poly_b = car_b.get_collision_polygon()

                    collided, normal, penetration = collide_polygons_sat(poly_a, poly_b)
                    if collided:
                        resolve_collision(car_a, car_b, normal, penetration)
        
        # Vérification et résolution des collisions entre voitures et murs
        for car in all_cars:
            if car.hp <= 0 and not car.is_disabled: # Ne pas vérifier les collisions pour les voitures détruites
                continue
            for wall in walls:
                poly_car = car.get_collision_polygon()
                # Utiliser le rect du mur pour une première vérification rapide
                if car.rect.colliderect(wall.rect):
                    collided, normal, penetration = collide_car_wall_sat(car, wall)
                    if collided:
                        resolve_collision(car, wall, normal, penetration)
        
        # --- Gestion des bonus de vie ---
        health_pickup_spawn_timer += dt
        if health_pickup_spawn_timer >= HEALTH_PICKUP_SPAWN_INTERVAL:
            health_pickup_spawn_timer = 0.0
            # Générer un point aléatoire sur l'écran
            x = random.randint(HEALTH_PICKUP_RADIUS, SCREEN_WIDTH - HEALTH_PICKUP_RADIUS)
            y = random.randint(HEALTH_PICKUP_RADIUS, SCREEN_HEIGHT - HEALTH_PICKUP_RADIUS)
            hp_value = random.randint(HEALTH_PICKUP_MIN_HP, HEALTH_PICKUP_MAX_HP)
            new_pickup = HealthPickup(x, y, hp_value)
            health_pickups.add(new_pickup)
            print(f"Bonus de vie apparu à ({x},{y}) avec {hp_value} PV.")

        # Collisions entre voitures et bonus de vie
        for car in all_cars:
            if car.hp > 0:
                collided_pickups = pygame.sprite.spritecollide(car, health_pickups, True, pygame.sprite.collide_circle_ratio(0.7))
                for pickup in collided_pickups:
                    car.heal(pickup.hp_value)
                    print(f"Voiture {car.color} a ramassé un bonus de vie de {pickup.hp_value} PV.")

        # --- Rendu ---
        screen.fill(DARK_GRAY) # Fond de la piste

        for wall in walls:
            wall.draw(screen)

        for car in all_cars:
            car.draw(screen)
        
        for pickup in health_pickups:
            pickup.draw(screen)

        # Affichage des scores
        score_text_car1 = font_score.render(f"Bleu: {car1.score}", True, BLUE)
        score_text_car2 = font_score.render(f"Rouge: {car2.score}", True, RED)
        screen.blit(score_text_car1, (10, 10))
        screen.blit(score_text_car2, (SCREEN_WIDTH - score_text_car2.get_width() - 10, 10))


        pygame.display.flip()

    pygame.quit()

# --- Exécution du jeu ---
if __name__ == "__main__":
    game_loop()
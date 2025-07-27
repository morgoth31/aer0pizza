import pygame
import random
import math # Added for car placement calculations
from constants import * # Import all constants
from car import Car
from health_pickup import HealthPickup
from wall import Wall
from collision_utils import collide_polygons_sat, collide_car_wall_sat, resolve_collision

# --- Main Menu Function ---
def main_menu(screen):
    font_title = pygame.font.Font(None, 74)
    font_options = pygame.font.Font(None, 48)
    
    title_text = font_title.render(GAME_TITLE, True, WHITE)
    
    # Initial menu options (will be updated in loop)
    option_1_player = font_options.render("Players: 1", True, WHITE)
    option_2_players = font_options.render("Players: 2", True, WHITE)
    ai_count_text = font_options.render(f"AI Opponents: 0", True, WHITE) # Initial text

    selected_player_option = 0 # 0 for 1 player, 1 for 2 players
    ai_count_value = 0 # 0 to 10
    menu_state = "player_count" # "player_count" or "ai_count"

    menu_select_sound = None
    try:
        menu_select_sound = pygame.mixer.Sound(SOUND_MENU_SELECT_PATH)
        menu_select_sound.set_volume(0.7)
    except pygame.error as e:
        print(f"Error loading menu sound: {e}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11: # Toggle Fullscreen
                    pygame.display.toggle_fullscreen()

                if menu_state == "player_count":
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        selected_player_option = 1 - selected_player_option # Toggle between 0 and 1
                        if menu_select_sound: menu_select_sound.play()
                    if event.key == pygame.K_RETURN:
                        if menu_select_sound: menu_select_sound.play()
                        menu_state = "ai_count"
                elif menu_state == "ai_count":
                    if event.key == pygame.K_UP:
                        ai_count_value = min(10, ai_count_value + 1)
                        if menu_select_sound: menu_select_sound.play()
                    if event.key == pygame.K_DOWN:
                        ai_count_value = max(0, ai_count_value - 1)
                        if menu_select_sound: menu_select_sound.play()
                    if event.key == pygame.K_RETURN:
                        if menu_select_sound: menu_select_sound.play()
                        # Return (number of players, number of AI opponents)
                        return (selected_player_option + 1), ai_count_value 
        
        # Update option colors and text based on current menu state
        if menu_state == "player_count":
            option_1_player = font_options.render("Players: 1", True, YELLOW if selected_player_option == 0 else WHITE)
            option_2_players = font_options.render("Players: 2", True, YELLOW if selected_player_option == 1 else WHITE)
            ai_count_text = font_options.render(f"AI Opponents: {ai_count_value}", True, WHITE) # Not active
        else: # menu_state == "ai_count"
            option_1_player = font_options.render("Players: 1", True, WHITE) # Not active
            option_2_players = font_options.render("Players: 2", True, WHITE) # Not active
            ai_count_text = font_options.render(f"AI Opponents: {ai_count_value}", True, YELLOW) # Active

        screen.fill(BLACK)
        
        # Center texts
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)))
        screen.blit(option_1_player, option_1_player.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)))
        screen.blit(option_2_players, option_2_players.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 0)))
        screen.blit(ai_count_text, ai_count_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)))
        
        # Dynamic prompt text
        if menu_state == "player_count":
            prompt_text = font_options.render("Use UP/DOWN to select players, ENTER to confirm", True, WHITE)
        else:
            prompt_text = font_options.render("Use UP/DOWN to adjust AI, ENTER to start game", True, WHITE)
        screen.blit(prompt_text, prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)))

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

# --- Main Game Loop Function ---
def game_loop():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

    # Get selected options from the main menu
    player_count, ai_count = main_menu(screen)
    print(f"Menu selection: Players = {player_count}, AI Opponents = {ai_count}")

    # Define the track walls (using constants for screen dimensions)
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

    player_cars = []
    ai_cars = []

    # Dynamic initial car placement
    # Calculate spawn area (inside inner track)
    track_inner_left = 150 + CAR_LENGTH
    track_inner_right = SCREEN_WIDTH - 150 - CAR_LENGTH
    track_inner_top = 150 + CAR_LENGTH
    track_inner_bottom = SCREEN_HEIGHT - 150 - CAR_LENGTH

    # Define a smaller, more central spawn area for AIs
    ai_spawn_width = (track_inner_right - track_inner_left) * 0.6 # 60% of inner track width
    ai_spawn_height = (track_inner_bottom - track_inner_top) * 0.6 # 60% of inner track height

    ai_spawn_center_x = SCREEN_WIDTH // 2
    ai_spawn_center_y = SCREEN_HEIGHT // 2

    ai_spawn_min_x = int(ai_spawn_center_x - ai_spawn_width / 2)
    print(ai_spawn_min_x)
    ai_spawn_max_x = int(ai_spawn_center_x + ai_spawn_width / 2)
    print(ai_spawn_max_x)
    ai_spawn_min_y = int(ai_spawn_center_y - ai_spawn_height / 2)
    print(ai_spawn_min_y)
    ai_spawn_max_y = int(ai_spawn_center_y + ai_spawn_height / 2)
    print(ai_spawn_max_y)

    # Place player cars
    # Player 1 (Blue)
    player_cars.append(Car(SCREEN_WIDTH // 2 - CAR_WIDTH, SCREEN_HEIGHT // 2 - CAR_LENGTH * 2, angle=0, color=BLUE, is_player=True))
    if player_count == 2:
        # Player 2 (Green)
        player_cars.append(Car(SCREEN_WIDTH // 2 + CAR_WIDTH, SCREEN_HEIGHT // 2 - CAR_LENGTH * 2, angle=0, color=GREEN, is_player=True))

    # Place AI cars randomly within the defined AI spawn area, avoiding initial player positions
    for i in range(ai_count):
        while True:
            
            x = random.randint(ai_spawn_min_x, ai_spawn_max_x)
            y = random.randint(ai_spawn_min_y, ai_spawn_max_y)
            print(f"Attempting to spawn AI Car {i+1} x={x}, y={y}")
            new_pos = pygame.math.Vector2(x, y)
            too_close = False
            # Check distance to all existing cars (players and other AIs)
            for car in player_cars + ai_cars:
                if (car.position - new_pos).length() < CAR_LENGTH * 2.5: # Increased buffer
                    too_close = True
                    break
            if not too_close:
                ai_cars.append(Car(x, y, angle=random.randint(0, 359), color=YELLOW, is_player=False))
                print(f"AI Car {i+1} spawned at: ({x}, {y})") # Added print statement for debugging
                break

    all_cars = pygame.sprite.Group(*(player_cars + ai_cars))
    print(f"Total cars in game: {len(all_cars.sprites())} (Players: {len(player_cars)}, AI: {len(ai_cars)})")

    health_pickups = pygame.sprite.Group() # Group for health pickups

    health_pickup_spawn_timer = 0.0
    font_score = pygame.font.Font(None, 36)
    font_coords = pygame.font.Font(None, COORD_FONT_SIZE) # Police pour les coordonnées

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
        # Handle inputs for all human players
        if player_count >= 1:
            player_cars[0].handle_input(keys, player_num=1)
        if player_count >= 2:
            player_cars[1].handle_input(keys, player_num=2)

        # AI updates for all AI cars
        for ai_car in ai_cars:
            target = None
            # Prioritize targeting active human players
            active_human_players = [p_car for p_car in player_cars if p_car.hp > 0]
            if active_human_players:
                # AI targets the closest active human player
                target = min(active_human_players, key=lambda p: (ai_car.position - p.position).length())
            elif health_pickups.sprites():
                # If no human players, target the closest health pickup
                target = min(health_pickups.sprites(), key=lambda p: (ai_car.position - p.position).length())
            
            ai_car.update_ai(target, dt)

        # --- Game Update ---
        for car in all_cars:
            car.update_physics(dt)

        # Check and resolve collisions between cars
        # Only consider cars that are alive or temporarily disabled for collision physics
        live_or_disabled_cars = [car for car in all_cars if car.hp > 0 or car.is_disabled]
        for i, car_a in enumerate(live_or_disabled_cars):
            for j, car_b in enumerate(live_or_disabled_cars):
                if i < j:
                    # If either car is disabled, they don't actively participate in new collisions
                    # (they can still be hit, but won't resolve movement against other disabled cars)
                    if car_a.is_disabled and car_b.is_disabled:
                        continue 

                    poly_a = car_a.get_collision_polygon()
                    poly_b = car_b.get_collision_polygon()

                    collided, normal, penetration = collide_polygons_sat(poly_a, poly_b)
                    if collided:
                        resolve_collision(car_a, car_b, normal, penetration)
        
        # Check and resolve collisions between cars and walls
        for car in all_cars:
            if car.hp <= 0 and not car.is_disabled: # Do not check collisions for destroyed cars
                continue
            for wall in walls:
                poly_car = car.get_collision_polygon()
                # Use wall's rect for a quick initial check
                if car.rect.colliderect(wall.rect):
                    collided, normal, penetration = collide_car_wall_sat(car, wall)
                    if collided:
                        resolve_collision(car, wall, normal, penetration)
        
        # --- Health Pickup Management ---
        health_pickup_spawn_timer += dt
        if health_pickup_spawn_timer >= HEALTH_PICKUP_SPAWN_INTERVAL:
            health_pickup_spawn_timer = 0.0
            # Générer un point aléatoire sur l'écran
            # Ensure pickups don't spawn too close to walls
            x = random.randint(ai_spawn_min_x, ai_spawn_max_x) # Utilise la zone de spawn des IA pour les bonus
            y = random.randint(ai_spawn_min_y, ai_spawn_max_y)
            hp_value = random.randint(HEALTH_PICKUP_MIN_HP, HEALTH_PICKUP_MAX_HP)
            new_pickup = HealthPickup(x, y, hp_value)
            health_pickups.add(new_pickup)
            print(f"Bonus de vie apparu à ({x},{y}) avec {hp_value} PV.")

        # Collisions entre voitures et bonus de vie
        for car in all_cars:
            if car.hp > 0: # Only active cars can pick up health
                collided_pickups = pygame.sprite.spritecollide(car, health_pickups, True, pygame.sprite.collide_circle_ratio(0.7))
                for pickup in collided_pickups:
                    car.heal(pickup.hp_value)
                    print(f"Voiture {car.color} a ramassé un bonus de vie de {pickup.hp_value} PV.")

        # --- Rendu ---
        screen.fill(DARK_GRAY) # Fond de la piste

        for wall in walls:
            wall.draw(screen)

        for pickup in health_pickups:
            pickup.draw(screen)

        for car in all_cars:
            car.draw(screen)
        
        # Display scores and HP for all cars
        score_y_offset = 10
        for i, car in enumerate(player_cars):
            status = " (Disabled)" if car.is_disabled else ""
            score_text = font_score.render(f"P{i+1} ({car.color}): Score: {car.score} HP: {car.hp:.0f}{status}", True, car.color)
            screen.blit(score_text, (10, score_y_offset + i * 40)) # Augmenté le décalage Y pour faire de la place aux coordonnées
            
            # Affichage des coordonnées des joueurs dans le coin supérieur gauche
            coord_text = font_coords.render(f"Coords: ({int(car.position.x)}, {int(car.position.y)})", True, car.color)
            screen.blit(coord_text, (10, score_y_offset + i * 40 + 25)) # Décalé sous le score

        ai_score_y_offset = 10
        for i, car in enumerate(ai_cars):
            status = " (Disabled)" if car.is_disabled else ""
            score_text = font_score.render(f"AI {i+1} ({car.color}): Score: {car.score} HP: {car.hp:.0f}{status}", True, YELLOW)
            screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, ai_score_y_offset + i * 40)) # Augmenté le décalage Y
            
            # Affichage des coordonnées des IA dans le coin supérieur droit
            coord_text = font_coords.render(f"Coords: ({int(car.position.x)}, {int(car.position.y)})", True, YELLOW)
            screen.blit(coord_text, (SCREEN_WIDTH - coord_text.get_width() - 10, ai_score_y_offset + i * 40 + 25)) # Décalé sous le score


        pygame.display.flip()

    pygame.quit()

# --- Run the game ---
if __name__ == "__main__":
    game_loop()

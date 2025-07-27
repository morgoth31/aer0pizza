import pygame
import random
import math # Added for car placement calculations
from constants import * # Import all constants
from car import Car, Bullet # Import Car class and now Bullet class
from health_pickup import HealthPickup # Import HealthPickup class
from wall import Wall # Import Wall class from wall.py
from collision_utils import collide_polygons_sat, collide_car_wall_sat, resolve_collision # Import collision functions

# --- Main Menu Function ---
def main_menu(screen):
    font_title = pygame.font.Font(None, 74)
    font_options = pygame.font.Font(None, 48)
    
    title_text = font_title.render(GAME_TITLE, True, WHITE)
    
    # Menu states and options
    menu_state = "game_mode" # "game_mode", "player_count", "ai_count", "difficulty"
    
    selected_game_mode = GAME_MODE_FREE_PLAY # Default
    selected_player_count = 1 # Default
    selected_ai_count = 0 # Default
    selected_difficulty = DIFFICULTY_MEDIUM # Default

    game_mode_options = [
        ("Free Play", GAME_MODE_FREE_PLAY),
        ("Race Mode", GAME_MODE_RACE)
    ]
    selected_game_mode_index = 0

    player_count_options = [1, 2]
    selected_player_count_index = 0

    difficulty_options = [
        DIFFICULTY_EASY,
        DIFFICULTY_MEDIUM,
        DIFFICULTY_HARD,
        DIFFICULTY_PRO
    ]
    selected_difficulty_index = 1 # Default to Medium

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
            if event.type == pygame.K_F11: # Toggle Fullscreen
                pygame.display.toggle_fullscreen()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if menu_select_sound: menu_select_sound.play()
                    if menu_state == "game_mode":
                        selected_game_mode_index = (selected_game_mode_index - 1) % len(game_mode_options)
                        selected_game_mode = game_mode_options[selected_game_mode_index][1]
                    elif menu_state == "player_count":
                        selected_player_count_index = (selected_player_count_index - 1) % len(player_count_options)
                        selected_player_count = player_count_options[selected_player_count_index]
                    elif menu_state == "ai_count":
                        selected_ai_count = min(10, selected_ai_count + 1)
                    elif menu_state == "difficulty":
                        selected_difficulty_index = (selected_difficulty_index - 1) % len(difficulty_options)
                        selected_difficulty = difficulty_options[selected_difficulty_index]


                elif event.key == pygame.K_DOWN:
                    if menu_select_sound: menu_select_sound.play()
                    if menu_state == "game_mode":
                        selected_game_mode_index = (selected_game_mode_index + 1) % len(game_mode_options)
                        selected_game_mode = game_mode_options[selected_game_mode_index][1]
                    elif menu_state == "player_count":
                        selected_player_count_index = (selected_player_count_index + 1) % len(player_count_options)
                        selected_player_count = player_count_options[selected_player_count_index]
                    elif menu_state == "ai_count":
                        selected_ai_count = max(0, selected_ai_count - 1)
                    elif menu_state == "difficulty":
                        selected_difficulty_index = (selected_difficulty_index + 1) % len(difficulty_options)
                        selected_difficulty = difficulty_options[selected_difficulty_index]

                elif event.key == pygame.K_RETURN:
                    if menu_select_sound: menu_select_sound.play()
                    if menu_state == "game_mode":
                        menu_state = "player_count"
                    elif menu_state == "player_count":
                        if selected_game_mode == GAME_MODE_RACE:
                            menu_state = "difficulty" # Go to difficulty for race mode
                        else:
                            menu_state = "ai_count" # For Free Play, choose AI count
                    elif menu_state == "ai_count":
                        # If we are in Free Play and chose AI count, or in Race Mode and chose AI count
                        return selected_player_count, selected_ai_count, selected_game_mode, selected_difficulty
                    elif menu_state == "difficulty":
                        # This state is only reached from Race Mode -> Player Count -> Difficulty
                        # After selecting difficulty, we need to go to AI count if in Race mode
                        # This ensures the flow: Mode -> Players -> Difficulty -> AI Count -> Start
                        menu_state = "ai_count" # Now go to AI count for race mode
                
                # Gérer la touche Échap pour revenir au menu précédent
                elif event.key == pygame.K_ESCAPE:
                    if menu_select_sound: menu_select_sound.play()
                    if menu_state == "difficulty":
                        menu_state = "player_count" # From difficulty, go back to player count
                    elif menu_state == "ai_count":
                        if selected_game_mode == GAME_MODE_RACE:
                            menu_state = "difficulty" # From AI count in Race mode, go back to difficulty
                        else:
                            menu_state = "player_count" # From AI count in Free Play, go back to player count
                    elif menu_state == "player_count":
                        menu_state = "game_mode" # From player count, go back to game mode selection
                    elif menu_state == "game_mode":
                        return None, None, None, None # Signal to quit the application
        
        screen.fill(BLACK)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)))

        # Display options based on current menu_state
        if menu_state == "game_mode":
            for i, (text, mode) in enumerate(game_mode_options):
                option_text = font_options.render(f"Game Mode: {text}", True, YELLOW if i == selected_game_mode_index else WHITE)
                screen.blit(option_text, option_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50 + i * 50)))
            prompt_text = font_options.render("Use UP/DOWN to select mode, ENTER to confirm, ESC to quit", True, WHITE) # Updated prompt
            screen.blit(prompt_text, prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)))

        elif menu_state == "player_count":
            for i, count in enumerate(player_count_options):
                option_text = font_options.render(f"Players: {count}", True, YELLOW if i == selected_player_count_index else WHITE)
                screen.blit(option_text, option_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50 + i * 50)))
            prompt_text = font_options.render("Use UP/DOWN to select players, ENTER to confirm, ESC to go back", True, WHITE) # Updated prompt
            screen.blit(prompt_text, prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)))

        elif menu_state == "ai_count":
            ai_count_text = font_options.render(f"AI Opponents: {selected_ai_count}", True, YELLOW)
            screen.blit(ai_count_text, ai_count_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
            prompt_text = font_options.render("Use UP/DOWN to adjust AI, ENTER to start game, ESC to go back", True, WHITE) # Updated prompt
            screen.blit(prompt_text, prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)))
            # If in Race mode, show difficulty selection as well
            if selected_game_mode == GAME_MODE_RACE:
                difficulty_text_display = font_options.render(f"Difficulty: {selected_difficulty.capitalize()}", True, WHITE)
                screen.blit(difficulty_text_display, difficulty_text_display.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)))

        elif menu_state == "difficulty":
            for i, diff in enumerate(difficulty_options):
                option_text = font_options.render(f"Difficulty: {diff.capitalize()}", True, YELLOW if i == selected_difficulty_index else WHITE)
                screen.blit(option_text, option_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50 + i * 50)))
            prompt_text = font_options.render("Use UP/DOWN to select difficulty, ENTER to confirm, ESC to go back", True, WHITE) # Updated prompt
            screen.blit(prompt_text, prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)))

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)
    
    # Fallback return in case loop exits unexpectedly
    return selected_player_count, selected_ai_count, selected_game_mode, selected_difficulty


# --- Main Game Loop Function (renamed to run_game_session) ---
def run_game_session(screen, player_count, ai_count, game_mode, difficulty):
    # Initialisation de l'écran et de l'horloge (déjà fait dans le bloc principal)
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

    # Define the track walls with explicit normals (pointing outwards from the track)
    # Each tuple: (start_point, end_point, normal_vector)
    track_walls_data = [
        # Outer Walls (Defined counter-clockwise for normal to point outward)
        ((50, 50), (50, SCREEN_HEIGHT - 50), pygame.math.Vector2(-1, 0)), # Left Outer (normal points left)
        ((50, SCREEN_HEIGHT - 50), (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50), pygame.math.Vector2(0, 1)), # Bottom Outer (normal points down)
        ((SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50), (SCREEN_WIDTH - 50, 50), pygame.math.Vector2(1, 0)), # Right Outer (normal points right)
        ((SCREEN_WIDTH - 50, 50), (50, 50), pygame.math.Vector2(0, -1)), # Top Outer (normal points up)

        # Inner Walls (Defined clockwise for normal to point outward from the track, i.e., inwards from the wall segment)
        ((150, 150), (SCREEN_WIDTH - 150, 150), pygame.math.Vector2(0, 1)), # Top Inner (normal points down, into track)
        ((SCREEN_WIDTH - 150, 150), (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150), pygame.math.Vector2(-1, 0)), # Right Inner (normal points left, into track)
        ((SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150), (150, SCREEN_HEIGHT - 150), pygame.math.Vector2(0, -1)), # Bottom Inner (normal points up, into track)
        ((150, SCREEN_HEIGHT - 150), (150, 150), pygame.math.Vector2(1, 0)) # Left Inner (normal points right, into track)
    ]
    walls = pygame.sprite.Group()
    for p1, p2, normal in track_walls_data:
        walls.add(Wall(p1, p2, normal)) # Pass the normal vector to the Wall constructor

    # Define waypoints for race mode (simple rectangular path for now)
    # These points should be inside the track and follow the racing line
    TRACK_WAYPOINTS = [
        (SCREEN_WIDTH // 2, 120), # Start line / Top middle (inside track)
        (SCREEN_WIDTH - 120, 120), # Top right corner (inside track)
        (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120), # Bottom right corner (inside track)
        (120, SCREEN_HEIGHT - 120), # Bottom left corner (inside track)
        (120, 120) # Top left corner (inside track, completing the loop)
    ]


    player_cars = []
    ai_cars = []
    all_bullets = pygame.sprite.Group() # Group to manage all bullets

    # Dynamic initial car placement based on game mode
    if game_mode == GAME_MODE_RACE:
        # Starting line placement
        # Place cars horizontally near the top inner wall, facing down (angle=180)
        total_cars_on_start = player_count + ai_count
        start_x_spacing = CAR_WIDTH * 1.5
        start_x_base = SCREEN_WIDTH // 2 - (start_x_spacing * (total_cars_on_start - 1)) / 2
        start_y = 200 # A bit below the top inner wall, on the track

        current_car_index = 0
        for i in range(player_count):
            x_pos = start_x_base + current_car_index * start_x_spacing
            player_cars.append(Car(x_pos, start_y, angle=180, color=BLUE if i == 0 else GREEN, is_player=True, game_mode=game_mode, difficulty=difficulty))
            current_car_index += 1
        
        for i in range(ai_count):
            x_pos = start_x_base + current_car_index * start_x_spacing
            ai_cars.append(Car(x_pos, start_y, angle=180, color=YELLOW, is_player=False, game_mode=game_mode, difficulty=difficulty))
            current_car_index += 1

    else: # GAME_MODE_FREE_PLAY
        # Calculate spawn area (inside inner track)
        spawn_min_x = 150 + CAR_LENGTH
        spawn_max_x = SCREEN_WIDTH - 150 - CAR_LENGTH
        spawn_min_y = 150 + CAR_LENGTH
        spawn_max_y = SCREEN_HEIGHT - 150 - CAR_LENGTH

        # Place player cars
        player_cars.append(Car(SCREEN_WIDTH // 2 - CAR_WIDTH, SCREEN_HEIGHT // 2 - CAR_LENGTH * 2, angle=0, color=BLUE, is_player=True, game_mode=game_mode, difficulty=difficulty))
        if player_count == 2:
            player_cars.append(Car(SCREEN_WIDTH // 2 + CAR_WIDTH, SCREEN_HEIGHT // 2 - CAR_LENGTH * 2, angle=0, color=GREEN, is_player=True, game_mode=game_mode, difficulty=difficulty))

        # Place AI cars randomly within the track boundaries, avoiding initial player positions
        for i in range(ai_count):
            while True:
                x = random.randint(spawn_min_x, spawn_max_x)
                y = random.randint(spawn_min_y, spawn_max_y)
                new_pos = pygame.math.Vector2(x, y)
                too_close = False
                # Check distance to all existing cars (players and other AIs)
                for car in player_cars + ai_cars:
                    if (car.position - new_pos).length() < CAR_LENGTH * 2.5: # Increased buffer
                        too_close = True
                        break
                if not too_close:
                    ai_cars.append(Car(x, y, angle=random.randint(0, 359), color=YELLOW, is_player=False, game_mode=game_mode, difficulty=difficulty))
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
                return False # Signal to quit the application
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11: # Toggle Fullscreen
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE: # NOUVEAU: Retour au menu principal
                    return True # Signal to go back to the main menu

        keys = pygame.key.get_pressed()
        # Handle inputs for all human players and collect bullets
        if player_count >= 1:
            bullet_p1 = player_cars[0].handle_input(keys, player_num=1)
            if bullet_p1:
                all_bullets.add(bullet_p1)
        if player_count >= 2:
            bullet_p2 = player_cars[1].handle_input(keys, player_num=2)
            if bullet_p2:
                all_bullets.add(bullet_p2)

        # AI updates for all AI cars and collect bullets
        for ai_car in ai_cars:
            if game_mode == GAME_MODE_RACE:
                bullet_ai = ai_car.update_ai(None, dt, track_waypoints=TRACK_WAYPOINTS) # No direct target, follow waypoints
            else: # Free Play mode
                target = None
                # Prioritize targeting active human players
                active_human_players = [p_car for p_car in player_cars if p_car.hp > 0]
                if active_human_players:
                    # AI targets the closest active human player
                    target = min(active_human_players, key=lambda p: (ai_car.position - p.position).length())
                elif health_pickups.sprites():
                    # If no human players, target the closest health pickup
                    target = min(health_pickups.sprites(), key=lambda p: (ai_car.position - p.position).length())
                
                bullet_ai = ai_car.update_ai(target, dt)
            
            if bullet_ai:
                all_bullets.add(bullet_ai)


        # --- Game Update ---
        for car in all_cars:
            car.update_physics(dt)
        
        for bullet in all_bullets:
            bullet.update(dt)

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
        
        # Collisions balles-voitures
        bullets_to_remove = []
        for bullet in all_bullets:
            for car in all_cars:
                # Prevent bullet from hitting its own car
                if car.color == bullet.owner_car_color:
                    continue
                
                # Vérification plus précise de la collision
                # D'abord un test rapide avec les rects
                if pygame.sprite.collide_rect(bullet, car):
                    # Ensuite un test plus précis avec les polygones
                    car_poly = car.get_collision_polygon()
                    bullet_pos = pygame.math.Vector2(bullet.position)
                    
                    # Vérifier la distance entre la balle et chaque segment du polygone de la voiture
                    for i in range(len(car_poly)):
                        p1 = car_poly[i]
                        p2 = car_poly[(i + 1) % len(car_poly)]
                        
                        # Distance point-segment
                        segment = p2 - p1
                        to_point = bullet_pos - p1
                        segment_length = segment.length()
                        segment = segment.normalize()
                        
                        projection = to_point.dot(segment)
                        projection = max(0, min(projection, segment_length))
                        closest_point = p1 + segment * projection
                        
                        distance = (bullet_pos - closest_point).length()
                        
                        if distance <= bullet.radius:
                            car.take_damage(bullet.damage * 100, bullet.position)
                            bullets_to_remove.append(bullet)
                            break

        # Collisions balles-murs
        for bullet in all_bullets:
            for wall in walls:
                # Check for collision between bullet (circle) and wall (line segment)
                # This is a simplified check, a more accurate one would use line-circle intersection
                # For now, if bullet rect overlaps wall rect, consider it a hit
                if pygame.sprite.collide_rect(bullet, wall):
                    bullets_to_remove.append(bullet)
                    break

        for bullet in bullets_to_remove:
            if bullet in all_bullets: # Ensure it's still in the group before removing
                all_bullets.remove(bullet)

        # --- Health Pickup Management ---
        # Health pickups only spawn in Free Play mode
        if game_mode == GAME_MODE_FREE_PLAY:
            health_pickup_spawn_timer += dt
            if health_pickup_spawn_timer >= HEALTH_PICKUP_SPAWN_INTERVAL:
                health_pickup_spawn_timer = 0.0
                # Générer un point aléatoire sur l'écran
                # Ensure pickups don't spawn too close to walls
                x = random.randint(150 + HEALTH_PICKUP_RADIUS, SCREEN_WIDTH - 150 - HEALTH_PICKUP_RADIUS)
                y = random.randint(150 + HEALTH_PICKUP_RADIUS, SCREEN_HEIGHT - 150 - HEALTH_PICKUP_RADIUS)
                hp_value = random.randint(HEALTH_PICKUP_MIN_HP, HEALTH_PICKUP_MAX_HP)
                new_pickup = HealthPickup(x, y, hp_value)
                health_pickups.add(new_pickup)
                print(f"Bonus de vie apparu à ({x},{y}) avec {hp_value} PV.")

            # Collisions entre voitures et bonus de vie
            for car in all_cars:
                if car.hp > 0: # Only active cars can pick up health
                    # Utilisation de la nouvelle constante HEALTH_PICKUP_COLLISION_RATIO
                    collided_pickups = pygame.sprite.spritecollide(car, health_pickups, True, pygame.sprite.collide_circle_ratio(HEALTH_PICKUP_COLLISION_RATIO))
                    for pickup in collided_pickups:
                        car.heal(pickup.hp_value)
                        print(f"Voiture {car.color} a ramassé un bonus de vie de {pickup.hp_value} PV.")

        # --- Rendu ---
        screen.fill(DARK_GRAY) # Fond de la piste

        for wall in walls:
            wall.draw(screen)
            # Dessiner la normale du mur pour le débogage (en rouge)
            wall_center = (wall.p1 + wall.p2) / 2
            pygame.draw.line(screen, RED, wall_center, wall_center + wall.normal * 30, 2) # Dessine la normale

        # Draw waypoints for debugging in Race Mode
        if game_mode == GAME_MODE_RACE:
            for i, wp in enumerate(TRACK_WAYPOINTS):
                pygame.draw.circle(screen, BLUE, wp, 10, 2) # Draw waypoint circle
                font_wp = pygame.font.Font(None, 20)
                wp_text = font_wp.render(str(i), True, BLUE)
                screen.blit(wp_text, wp_text.get_rect(center=(wp[0], wp[1] - 15)))


        for pickup in health_pickups:
            pickup.draw(screen)

        for car in all_cars:
            car.draw(screen)
        
        for bullet in all_bullets: # Draw all active bullets
            bullet.draw(screen)

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

    return False # Default return if loop exits without ESC (e.g., QUIT event)

# --- Run the game ---
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        player_count, ai_count, game_mode, difficulty = main_menu(screen)
        
        # If main_menu signals to quit (ESC pressed on game_mode screen)
        if game_mode is None:
            break 
        
        # Run the game session
        return_to_menu = run_game_session(screen, player_count, ai_count, game_mode, difficulty)
        
        # If run_game_session returns False, it means QUIT event was triggered, so break
        if not return_to_menu:
            break

    pygame.quit()

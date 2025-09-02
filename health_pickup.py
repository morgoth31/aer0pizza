import pygame
from constants import * # Import all constants

class HealthPickup(pygame.sprite.Sprite):
    """
    Represents a health pickup in the game.
    """
    def __init__(self, x, y, hp_value):
        """
        Initializes a new HealthPickup object.

        Args:
            x (int): The x-coordinate of the health pickup's position.
            y (int): The y-coordinate of the health pickup's position.
            hp_value (int): The amount of HP the pickup restores.
        """
        super().__init__()
        self.position = pygame.math.Vector2(x, y)
        self.hp_value = hp_value
        self.radius = HEALTH_PICKUP_RADIUS
        self.color = GREEN # Health pickup color
        self.font = pygame.font.Font(None, 20)
        self.text_surface = self.font.render(f"+{hp_value}", True, WHITE)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        """
        Draws the health pickup on the screen.

        Args:
            screen (pygame.Surface): The screen to draw the health pickup on.
        """
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.position.x), int(self.position.y)), self.radius, 1) # Outline
        screen.blit(self.text_surface, self.text_surface.get_rect(center=(int(self.position.x), int(self.position.y))))

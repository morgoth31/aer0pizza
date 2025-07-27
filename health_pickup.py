import pygame
from constants import * # Import all constants

class HealthPickup(pygame.sprite.Sprite):
    def __init__(self, x, y, hp_value):
        super().__init__()
        self.position = pygame.math.Vector2(x, y)
        self.hp_value = hp_value
        self.radius = HEALTH_PICKUP_RADIUS
        self.color = GREEN # Health pickup color
        self.font = pygame.font.Font(None, 20)
        self.text_surface = self.font.render(f"+{hp_value}", True, WHITE)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        """Draws the health pickup."""
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.position.x), int(self.position.y)), self.radius, 1) # Outline
        screen.blit(self.text_surface, self.text_surface.get_rect(center=(int(self.position.x), int(self.position.y))))

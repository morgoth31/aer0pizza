import pygame
from constants import WALL_COLOR # Import WALL_COLOR from constants

class Wall(pygame.sprite.Sprite):
    def __init__(self, p1, p2, normal_vector, thickness=10, color=WALL_COLOR):
        super().__init__()
        self.p1 = pygame.math.Vector2(p1)
        self.p2 = pygame.math.Vector2(p2)
        self.normal = normal_vector.normalize()
        self.thickness = thickness
        self.color = color
        
        # Calcul du rect englobant
        min_x = min(self.p1.x, self.p2.x) - self.thickness
        max_x = max(self.p1.x, self.p2.x) + self.thickness
        min_y = min(self.p1.y, self.p2.y) - self.thickness
        max_y = max(self.p1.y, self.p2.y) + self.thickness
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def get_collision_line_segment(self):
        """Retourne le segment de ligne et sa normale pour la collision."""
        return self.p1, self.p2, self.normal

    def draw(self, screen):
        """Dessine le mur."""
        pygame.draw.line(screen, self.color, self.p1, self.p2, self.thickness)


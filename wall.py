import pygame
from constants import * # Import all constants

class Wall(pygame.sprite.Sprite):
    def __init__(self, p1, p2, thickness=10, color=WALL_COLOR):
        super().__init__()
        self.p1 = pygame.math.Vector2(p1)
        self.p2 = pygame.math.Vector2(p2)
        self.thickness = thickness
        self.color = color

        # Calculate wall normal (pointing outwards from the track)
        edge = self.p2 - self.p1
        self.normal = pygame.math.Vector2(-edge.y, edge.x).normalize()
        
        # Calculate bounding rect for drawing and initial collision approximation
        min_x = min(self.p1.x, self.p2.x) - thickness / 2
        max_x = max(self.p1.x, self.p2.x) + thickness / 2
        min_y = min(self.p1.y, self.p2.y) - thickness / 2
        max_y = max(self.p1.y, self.p2.y) + thickness / 2
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def get_collision_line_segment(self):
        """Returns the line segment and its normal for collision."""
        return self.p1, self.p2, self.normal

    def draw(self, screen):
        """Draws the wall."""
        pygame.draw.line(screen, self.color, self.p1, self.p2, self.thickness)

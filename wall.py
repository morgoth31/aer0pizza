import pygame
from constants import WALL_COLOR # Import WALL_COLOR from constants

class Wall(pygame.sprite.Sprite):
    """
    Represents a wall in the game.
    """
    def __init__(self, p1, p2, normal_vector, thickness=10, color=WALL_COLOR):
        """
        Initializes a new Wall object.

        Args:
            p1 (tuple): The starting point of the wall.
            p2 (tuple): The ending point of the wall.
            normal_vector (pygame.math.Vector2): The normal vector of the wall.
            thickness (int, optional): The thickness of the wall. Defaults to 10.
            color (tuple, optional): The color of the wall. Defaults to WALL_COLOR.
        """
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
        """
        Returns the line segment and its normal for collision detection.

        Returns:
            tuple: A tuple containing the start point, end point, and normal vector of the wall.
        """
        return self.p1, self.p2, self.normal

    def draw(self, screen):
        """
        Draws the wall on the screen.

        Args:
            screen (pygame.Surface): The screen to draw the wall on.
        """
        pygame.draw.line(screen, self.color, self.p1, self.p2, self.thickness)


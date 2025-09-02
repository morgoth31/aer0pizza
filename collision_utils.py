import pygame
import math
from constants import * # Import all constants
# We will need to import Car class for type checking in resolve_collision,
# but to avoid circular import, we'll import it inside the function if needed,
# or assume it's passed correctly. For now, let's keep it simple.
# If a circular import issue arises, a common pattern is to import at the function level
# or use a type hint string "Car" and import only for type checking (from typing import TYPE_CHECKING).

def project_polygon(axis, polygon_points):
    """
    Projects a polygon onto an axis and returns the interval [min, max].

    Args:
        axis (pygame.math.Vector2): The axis to project onto.
        polygon_points (list): A list of pygame.math.Vector2 objects representing the polygon's vertices.

    Returns:
        tuple: A tuple containing the minimum and maximum projection values.
    """
    min_proj = float('inf')
    max_proj = float('-inf')
    for p in polygon_points:
        proj = p.dot(axis)
        min_proj = min(min_proj, proj)
        max_proj = max(max_proj, proj)
    return min_proj, max_proj

def get_axes(polygon_points):
    """
    Returns the normal axes to each edge of a polygon.

    Args:
        polygon_points (list): A list of pygame.math.Vector2 objects representing the polygon's vertices.

    Returns:
        list: A list of pygame.math.Vector2 objects representing the normal axes.
    """
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
    Detects collision between two convex polygons using the Separating Axis Theorem (SAT).

    Args:
        poly1_points (list): A list of pygame.math.Vector2 objects representing the vertices of the first polygon.
        poly2_points (list): A list of pygame.math.Vector2 objects representing the vertices of the second polygon.

    Returns:
        tuple: A tuple containing a boolean indicating if a collision occurred,
               the collision normal (pygame.math.Vector2), and the penetration depth (float).
               Returns (False, None, None) if there is no collision.
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
    Detects collision between a car (polygon) and a wall (line segment) using SAT.

    Args:
        car (Car): The car object.
        wall (Wall): The wall object.

    Returns:
        tuple: A tuple containing a boolean indicating if a collision occurred,
               the collision normal (pygame.math.Vector2), and the penetration depth (float).
               Returns (False, None, None) if there is no collision.
    """
    car_points = car.get_collision_polygon()
    wall_p1, wall_p2, wall_normal = wall.get_collision_line_segment()

    # Convert wall segment to a "thick" polygon for SAT
    wall_thickness = wall.thickness
    wall_perp = pygame.math.Vector2(-wall_normal.y, wall_normal.x)
    
    # Create a polygon representing the thick wall
    wall_poly = [
        wall_p1 + wall_perp * wall_thickness/2,
        wall_p2 + wall_perp * wall_thickness/2,
        wall_p2 - wall_perp * wall_thickness/2,
        wall_p1 - wall_perp * wall_thickness/2
    ]
    
    # Use standard SAT between car polygon and wall polygon
    collided, normal, penetration = collide_polygons_sat(car_points, wall_poly)
    
    if collided:
        # Make sure normal points from car to wall
        car_center = sum(car_points, pygame.math.Vector2(0,0)) / len(car_points)
        wall_center = sum(wall_poly, pygame.math.Vector2(0,0)) / len(wall_poly)
        direction = wall_center - car_center
        if normal.dot(direction) < 0:
            normal *= -1
        
        return True, normal, penetration
    
    return False, None, None

def resolve_collision(obj1, obj2, normal, penetration):
    """
    Resolves a collision between two objects (car-car or car-wall).

    Args:
        obj1 (Car): The first object (always a car).
        obj2 (Car or Wall): The second object.
        normal (pygame.math.Vector2): The collision normal (unit vector).
        penetration (float): The penetration depth.
    """
    # Import Car here to avoid circular dependency at module level
    from car import Car 

    # 1. Separate objects (resolve penetration)
    if isinstance(obj2, Car): # Car-car collision
        total_inv_mass = (1 / obj1.mass) + (1 / obj2.mass)
        if total_inv_mass == 0: return

        resolution_vector = normal * penetration / total_inv_mass
        obj1.position -= resolution_vector / obj1.mass
        obj2.position += resolution_vector / obj2.mass
    else: # Car-wall collision (obj2 is a Wall)
        obj1.position -= normal * penetration

    # Update objects' rects and points after penetration resolution
    obj1.update_physics(0)
    if isinstance(obj2, Car):
        obj2.update_physics(0)

    # 2. Calculate impulse (only for cars)
    if isinstance(obj2, Car): # Car-car collision
        relative_velocity = obj2.velocity - obj1.velocity
    else: # Car-wall collision
        relative_velocity = -obj1.velocity # Relative velocity is just the opposite of the car's velocity

    vel_along_normal = relative_velocity.dot(normal)

    if vel_along_normal > 0: # If objects are already moving apart
        return

    e = COLLISION_ELASTICITY

    # Calculate scalar impulse
    if isinstance(obj2, Car):
        j = -(1 + e) * vel_along_normal
        j /= total_inv_mass
    else: # Car-wall collision (infinite mass for the wall)
        j = -(1 + e) * vel_along_normal * obj1.mass # J = -(1+e) * v_rel_n * m

    impulse = normal * j
    obj1.velocity -= impulse / obj1.mass
    if isinstance(obj2, Car):
        obj2.velocity += impulse / obj2.mass

    # 3. Resolve friction (simple)
    tangent = relative_velocity - (vel_along_normal * normal)
    if tangent.length() > 0:
        tangent = tangent.normalize()

    sf = COLLISION_FRICTION

    jt = -relative_velocity.dot(tangent)
    if isinstance(obj2, Car):
        jt /= total_inv_mass
    else: # Car-wall collision
        jt *= obj1.mass # Jt = -v_rel_t * m

    if abs(jt) > j * sf:
        jt = j * sf * (-1 if jt < 0 else 1)

    friction_impulse = tangent * jt
    obj1.velocity -= friction_impulse / obj1.mass
    if isinstance(obj2, Car):
        obj2.velocity += friction_impulse / obj2.mass

    # 4. Calculate damage
    impact_force = (j / pygame.time.get_ticks() * 1000) # Approximation of F = dp/dt

    if isinstance(obj2, Car): # Car-car damage
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
    else: # Car-wall damage
        obj1.take_damage(WALL_DAMAGE_FACTOR, obj1.position) # Impact point approximated by car position

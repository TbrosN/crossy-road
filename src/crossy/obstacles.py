"""Obstacles (cars and logs) logic."""

import random
from crossy.config import (
    GRID_WIDTH, CAR_SPEED_MIN, CAR_SPEED_MAX,
    LOG_SPEED_MIN, LOG_SPEED_MAX,
    CARS_PER_ROW, LOGS_PER_ROW,
    COLOR_CAR_RED, COLOR_CAR_BLUE, COLOR_CAR_ORANGE
)


class Obstacle:
    """Base class for moving obstacles."""

    def __init__(self, x, y, speed, direction, width=1, color=None):
        """
        Initialize an obstacle.
        
        Args:
            x: X position (can be float for smooth movement)
            y: Y position (grid coordinate)
            speed: Movement speed in cells per second
            direction: 1 for right, -1 for left
            width: Width in cells (default 1)
            color: RGB color tuple
        """
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction
        self.width = width
        self.color = color

    def update(self, dt):
        """
        Update obstacle position.
        
        Args:
            dt: Delta time in seconds
        """
        self.x += self.speed * self.direction * dt
        
        # Wrap around screen edges (accounting for width)
        if self.direction > 0 and self.x > GRID_WIDTH + self.width:
            self.x = -self.width
        elif self.direction < 0 and self.x < -self.width:
            self.x = GRID_WIDTH + self.width

    def get_grid_x(self):
        """Get the grid x coordinate (rounded)."""
        return int(round(self.x))
    
    def get_left_edge(self):
        """Get the left edge of the obstacle."""
        return self.x
    
    def get_right_edge(self):
        """Get the right edge of the obstacle."""
        return self.x + self.width


class Car(Obstacle):
    """A car obstacle on roads."""

    def __init__(self, x, y, speed, direction):
        """Initialize a car with random color."""
        color = random.choice([COLOR_CAR_RED, COLOR_CAR_BLUE, COLOR_CAR_ORANGE])
        super().__init__(x, y, speed, direction, width=1, color=color)


class Log(Obstacle):
    """A log obstacle on rivers that the player can ride."""

    def __init__(self, x, y, speed, direction, color, width=2.5):
        """Initialize a log with width."""
        super().__init__(x, y, speed, direction, width=width, color=color)


class ObstacleManager:
    """Manages all obstacles in the game."""

    def __init__(self):
        """Initialize obstacle manager."""
        self.obstacles = []

    def generate_for_row(self, row_y, terrain_type):
        """
        Generate obstacles for a specific row.
        
        Args:
            row_y: Y coordinate of the row
            terrain_type: Type of terrain for this row
        """
        from crossy.config import TERRAIN_ROAD, TERRAIN_RIVER, COLOR_LOG
        
        # Remove old obstacles for this row
        self.obstacles = [obs for obs in self.obstacles if obs.y != row_y]
        
        if terrain_type == TERRAIN_ROAD:
            # Generate cars
            num_cars = random.randint(*CARS_PER_ROW)
            speed = random.uniform(CAR_SPEED_MIN, CAR_SPEED_MAX)
            direction = random.choice([-1, 1])
            
            for i in range(num_cars):
                # Space cars evenly with some randomness
                spacing = GRID_WIDTH / num_cars
                x = i * spacing + random.uniform(-spacing * 0.3, spacing * 0.3)
                if direction < 0:
                    x = GRID_WIDTH - x
                
                car = Car(x, row_y, speed, direction)
                self.obstacles.append(car)
        
        elif terrain_type == TERRAIN_RIVER:
            # Generate logs
            num_logs = random.randint(*LOGS_PER_ROW)
            speed = random.uniform(LOG_SPEED_MIN, LOG_SPEED_MAX)
            direction = random.choice([-1, 1])
            
            for i in range(num_logs):
                # Space logs evenly
                spacing = GRID_WIDTH / num_logs
                x = i * spacing + random.uniform(-spacing * 0.2, spacing * 0.2)
                if direction < 0:
                    x = GRID_WIDTH - x
                
                log = Log(x, row_y, speed, direction, COLOR_LOG)
                self.obstacles.append(log)

    def update(self, dt):
        """
        Update all obstacles.
        
        Args:
            dt: Delta time in seconds
        """
        for obstacle in self.obstacles:
            obstacle.update(dt)

    def get_obstacles_at(self, grid_y):
        """
        Get all obstacles at a specific grid row.
        
        Args:
            grid_y: Y coordinate
        
        Returns:
            list: List of obstacles at this row
        """
        return [obs for obs in self.obstacles if obs.y == grid_y]

    def check_collision_with_car(self, player_x, player_y):
        """
        Check if player collides with any car.
        
        Args:
            player_x: Player X position (float, can be between cells)
            player_y: Player Y position
        
        Returns:
            bool: True if collision detected
        """
        # Player occupies 1 cell width
        player_left = player_x
        player_right = player_x + 1
        
        for obstacle in self.obstacles:
            if isinstance(obstacle, Car) and obstacle.y == player_y:
                car_left = obstacle.get_left_edge()
                car_right = obstacle.get_right_edge()
                
                # Check for overlap
                if player_left < car_right and player_right > car_left:
                    return True
        return False

    def get_log_at_position(self, player_x, player_y):
        """
        Get log at player's position (if any).
        Uses forgiving collision - player needs to be at least 25% on the log.
        
        Args:
            player_x: Player X position (float, can be between cells)
            player_y: Player Y position
        
        Returns:
            Log or None: Log object if player is on one, None otherwise
        """
        # Player occupies 1 cell width
        player_left = player_x
        player_right = player_x + 1
        player_width = 1.0
        
        for obstacle in self.obstacles:
            if isinstance(obstacle, Log) and obstacle.y == player_y:
                log_left = obstacle.get_left_edge()
                log_right = obstacle.get_right_edge()
                
                # Calculate overlap
                overlap_left = max(player_left, log_left)
                overlap_right = min(player_right, log_right)
                overlap = max(0, overlap_right - overlap_left)
                
                # If at least 25% of player is on the log, they're safe
                # (slightly more forgiving to account for floating point precision)
                if overlap >= player_width * 0.25:
                    return obstacle
        return None

    def clear(self):
        """Clear all obstacles."""
        self.obstacles.clear()

    def reset(self):
        """Reset obstacle manager."""
        self.clear()

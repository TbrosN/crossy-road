"""Obstacles (cars and logs) logic."""

import random
from crossy.config import (
    GRID_WIDTH, CAR_SPEED_MIN, CAR_SPEED_MAX,
    LOG_SPEED_MIN, LOG_SPEED_MAX,
    CARS_PER_ROW, LOGS_PER_ROW, TREES_PER_ROW,
    COLOR_CAR_RED, COLOR_CAR_BLUE, COLOR_CAR_ORANGE, COLOR_TREE,
    TRAIN_SPEED, TRAIN_WIDTH, TRAIN_SPAWN_INTERVAL_MIN, TRAIN_SPAWN_INTERVAL_MAX,
    TRAIN_WARNING_TIME, COLOR_TRAIN, TOTAL_ROWS
)


def get_progress(row_y):
    """
    Calculate progress based on row number.
    
    Progress goes from 0.0 (start, high row numbers) to 1.0 (furthest point, row 0).
    
    Args:
        row_y: Row Y coordinate
    
    Returns:
        float: Progress value between 0.0 and 1.0
    """
    playable_rows = TOTAL_ROWS - 5  # Bottom 5 rows are safe zone
    progress = 1.0 - (row_y / playable_rows)
    return max(0.0, min(1.0, progress))


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
    
    def get_collision_box(self):
        """
        Get the collision box.
        Returns (left, top, right, bottom) in grid coordinates.
        """
        return (
            self.x,
            self.y,
            self.x + self.width,
            self.y + 1
        )


class Car(Obstacle):
    """Base car obstacle on roads."""

    def __init__(self, x, y, speed, direction, width=1, color=None):
        """Initialize a car with random color if not specified."""
        if color is None:
            color = random.choice([COLOR_CAR_RED, COLOR_CAR_BLUE, COLOR_CAR_ORANGE])
        super().__init__(x, y, speed, direction, width=width, color=color)


class Truck(Car):
    """A large truck - 3 blocks wide."""

    def __init__(self, x, y, speed, direction):
        """Initialize a truck."""
        super().__init__(x, y, speed, direction, width=3, color=COLOR_CAR_ORANGE)


class Sedan(Car):
    """A medium sedan - 2 blocks wide."""

    def __init__(self, x, y, speed, direction):
        """Initialize a sedan."""
        super().__init__(x, y, speed, direction, width=2, color=COLOR_CAR_BLUE)


class SmartCar(Car):
    """A small smart car - 1 block wide."""

    def __init__(self, x, y, speed, direction):
        """Initialize a smart car."""
        super().__init__(x, y, speed, direction, width=1, color=COLOR_CAR_RED)


class Log(Obstacle):
    """A log obstacle on rivers that the player can ride."""

    def __init__(self, x, y, speed, direction, color, width=2.5):
        """Initialize a log with width."""
        super().__init__(x, y, speed, direction, width=width, color=color)


class Tree:
    """A static tree obstacle on grass that blocks player movement."""

    def __init__(self, x, y):
        """
        Initialize a tree at a fixed position.
        
        Args:
            x: X position (grid coordinate)
            y: Y position (grid coordinate)
        """
        self.x = x
        self.y = y
        self.color = COLOR_TREE

    def get_grid_x(self):
        """Get the grid x coordinate."""
        return self.x


class Train(Obstacle):
    """A train obstacle that covers the entire track."""

    def __init__(self, x, y, direction):
        """Initialize a train with direction."""
        super().__init__(x, y, TRAIN_SPEED, direction, width=TRAIN_WIDTH, color=COLOR_TRAIN)


class TrainTrack:
    """Manages train spawning for a single train track row."""

    def __init__(self, row_y, progress=0.5):
        """
        Initialize a train track with difficulty scaling.
        
        Args:
            row_y: Y coordinate of this train track
            progress: Game progress (0.0 to 1.0) for difficulty scaling
        """
        self.row_y = row_y
        self.progress = progress
        self.direction = random.choice([-1, 1])  # Train direction
        self.train = None  # Current active train (if any)
        
        # Scale spawn intervals with progress
        # Early (low progress): longer intervals (6-12s), Late: shorter intervals (4-8s)
        interval_scale = 1.0 - (0.3 * progress)  # 1.0 -> 0.7
        self.spawn_interval_min = TRAIN_SPAWN_INTERVAL_MIN * interval_scale + 1.0  # 6s -> 4.5s
        self.spawn_interval_max = TRAIN_SPAWN_INTERVAL_MAX * interval_scale + 2.0  # 12s -> 9s
        
        # Randomize initial state to make tracks feel independent
        # Early game: less aggressive initial spawns
        # 10-30% chance: spawn a train immediately (scales with progress)
        # 10-30% chance: show warning (scales with progress)
        # 40-80% chance: normal random interval
        immediate_spawn_chance = 0.10 + 0.20 * progress  # 10% -> 30%
        warning_chance = 0.10 + 0.20 * progress  # 10% -> 30%
        
        roll = random.random()
        if roll < immediate_spawn_chance:
            # Spawn train immediately at a random position on the track
            if self.direction > 0:
                x = random.uniform(-TRAIN_WIDTH, GRID_WIDTH * 0.3)
            else:
                x = random.uniform(GRID_WIDTH * 0.7, GRID_WIDTH + TRAIN_WIDTH)
            self.train = Train(x, row_y, self.direction)
            self.time_until_next_train = random.uniform(self.spawn_interval_min, self.spawn_interval_max)
            self.warning = False
        elif roll < immediate_spawn_chance + warning_chance:
            # Start with warning active (train coming very soon)
            self.time_until_next_train = random.uniform(0.5, TRAIN_WARNING_TIME)
            self.warning = True
        else:
            # Normal random interval
            self.time_until_next_train = random.uniform(self.spawn_interval_min, self.spawn_interval_max)
            self.warning = False

    def update(self, dt):
        """
        Update train track state.
        
        Args:
            dt: Delta time in seconds
        
        Returns:
            Train or None: New train if spawned, None otherwise
        """
        # If there's an active train and it's off screen, remove it
        if self.train is not None:
            if (self.direction > 0 and self.train.x > GRID_WIDTH + TRAIN_WIDTH) or \
               (self.direction < 0 and self.train.x < -TRAIN_WIDTH):
                self.train = None
                # Schedule next train using scaled intervals
                self.time_until_next_train = random.uniform(self.spawn_interval_min, self.spawn_interval_max)
                self.warning = False
        
        # If no train, count down to next spawn
        if self.train is None:
            self.time_until_next_train -= dt
            
            # Show warning when close to spawn time
            if self.time_until_next_train <= TRAIN_WARNING_TIME and not self.warning:
                self.warning = True
            
            # Spawn train when timer reaches zero
            if self.time_until_next_train <= 0:
                # Spawn train off screen on the appropriate side
                if self.direction > 0:
                    x = -TRAIN_WIDTH
                else:
                    x = GRID_WIDTH + TRAIN_WIDTH
                
                self.train = Train(x, self.row_y, self.direction)
                self.warning = False
                return self.train
        
        return None

    def get_train(self):
        """Get the current active train (if any)."""
        return self.train


class ObstacleManager:
    """Manages all obstacles in the game."""

    def __init__(self):
        """Initialize obstacle manager."""
        self.obstacles = []
        self.trees = []
        self.train_tracks = {}  # Maps row_y to TrainTrack object

    def generate_for_row(self, row_y, terrain_type):
        """
        Generate obstacles for a specific row with difficulty scaling.
        
        Obstacle density and speed scale with progress:
        - Early game: fewer, slower obstacles
        - Late game: more, faster obstacles
        
        Args:
            row_y: Y coordinate of the row
            terrain_type: Type of terrain for this row
        """
        from crossy.config import TERRAIN_ROAD, TERRAIN_RIVER, TERRAIN_GRASS, TERRAIN_TRAIN, COLOR_LOG
        
        # Remove old obstacles for this row
        self.obstacles = [obs for obs in self.obstacles if obs.y != row_y]
        self.trees = [tree for tree in self.trees if tree.y != row_y]
        
        # Remove old train track for this row if it exists
        if row_y in self.train_tracks:
            del self.train_tracks[row_y]
        
        # Get progress for difficulty scaling
        progress = get_progress(row_y)
        
        if terrain_type == TERRAIN_ROAD:
            # Scale car count with progress
            # Early: 1-2 cars, Late: 2-5 cars
            min_cars = 1 + int(progress * 1)  # 1 -> 2
            max_cars = 2 + int(progress * 3)  # 2 -> 5
            num_cars = random.randint(min_cars, max_cars)
            
            # Scale speed with progress
            # Early: slower cars (0.8-1.5), Late: faster (1.0-3.0)
            speed_min = CAR_SPEED_MIN * (0.8 + 0.2 * progress)
            speed_max = CAR_SPEED_MIN + (CAR_SPEED_MAX - CAR_SPEED_MIN) * (0.5 + 0.5 * progress)
            speed = random.uniform(speed_min, speed_max)
            direction = random.choice([-1, 1])
            
            for i in range(num_cars):
                # Space cars evenly with some randomness
                spacing = GRID_WIDTH / num_cars
                x = i * spacing + random.uniform(-spacing * 0.3, spacing * 0.3)
                if direction < 0:
                    x = GRID_WIDTH - x
                
                # Randomly choose car type (more trucks at higher progress)
                truck_weight = 0.1 + 0.2 * progress  # 0.1 -> 0.3
                sedan_weight = 0.4
                smart_weight = 0.5 - 0.1 * progress  # 0.5 -> 0.4
                
                car_type = random.choices(
                    [SmartCar, Sedan, Truck],
                    weights=[smart_weight, sedan_weight, truck_weight],
                    k=1
                )[0]
                car = car_type(x, row_y, speed, direction)
                self.obstacles.append(car)
        
        elif terrain_type == TERRAIN_RIVER:
            # Scale log count inversely with progress (fewer logs = harder)
            # Early: 3-4 logs (easier), Late: 2-3 logs (harder)
            min_logs = max(2, 3 - int(progress * 1))  # 3 -> 2
            max_logs = max(3, 4 - int(progress * 1))  # 4 -> 3
            num_logs = random.randint(min_logs, max_logs)
            
            # Scale speed with progress (faster = harder)
            speed_min = LOG_SPEED_MIN * (0.8 + 0.4 * progress)
            speed_max = LOG_SPEED_MIN + (LOG_SPEED_MAX - LOG_SPEED_MIN) * (0.6 + 0.4 * progress)
            speed = random.uniform(speed_min, speed_max)
            direction = random.choice([-1, 1])
            
            for i in range(num_logs):
                # Space logs evenly
                spacing = GRID_WIDTH / num_logs
                x = i * spacing + random.uniform(-spacing * 0.2, spacing * 0.2)
                if direction < 0:
                    x = GRID_WIDTH - x
                
                log = Log(x, row_y, speed, direction, COLOR_LOG)
                self.obstacles.append(log)
        
        elif terrain_type == TERRAIN_GRASS:
            # Scale tree count with progress (more trees = harder navigation)
            # Early: 0-2 trees, Late: 0-4 trees
            min_trees = 0
            max_trees = 2 + int(progress * 2)  # 2 -> 4
            num_trees = random.randint(min_trees, max_trees)
            
            if num_trees > 0:
                # Generate random positions for trees (avoid duplicates)
                positions = random.sample(range(GRID_WIDTH), num_trees)
                for x in positions:
                    tree = Tree(x, row_y)
                    self.trees.append(tree)
        
        elif terrain_type == TERRAIN_TRAIN:
            # Create a train track for this row
            train_track = TrainTrack(row_y, progress)
            self.train_tracks[row_y] = train_track
            
            # If the train track already has a train, add it to obstacles
            if train_track.train is not None:
                self.obstacles.append(train_track.train)

    def update(self, dt):
        """
        Update all obstacles.
        
        Args:
            dt: Delta time in seconds
        """
        for obstacle in self.obstacles:
            obstacle.update(dt)
        
        # Update train tracks and spawn trains
        for train_track in list(self.train_tracks.values()):
            new_train = train_track.update(dt)
            if new_train is not None:
                self.obstacles.append(new_train)

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

    def check_collision_with_train(self, player_x, player_y):
        """
        Check if player collides with any train.
        
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
            if isinstance(obstacle, Train) and obstacle.y == player_y:
                train_left = obstacle.get_left_edge()
                train_right = obstacle.get_right_edge()
                
                # Check for overlap
                if player_left < train_right and player_right > train_left:
                    return True
        return False

    def is_train_warning(self, grid_y):
        """
        Check if there's a train warning for a specific row.
        
        Args:
            grid_y: Y coordinate
        
        Returns:
            bool: True if train warning is active
        """
        if grid_y in self.train_tracks:
            return self.train_tracks[grid_y].warning
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

    def has_tree_at(self, grid_x, grid_y):
        """
        Check if there's a tree at a specific grid position.
        
        Args:
            grid_x: X grid coordinate
            grid_y: Y grid coordinate
        
        Returns:
            bool: True if there's a tree at this position
        """
        for tree in self.trees:
            if tree.x == grid_x and tree.y == grid_y:
                return True
        return False

    def clear(self):
        """Clear all obstacles."""
        self.obstacles.clear()
        self.trees.clear()
        self.train_tracks.clear()

    def reset(self):
        """Reset obstacle manager."""
        self.clear()

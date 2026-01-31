"""Game state management."""

import os
from crossy.config import (
    GRID_WIDTH, GRID_HEIGHT, HIGH_SCORE_FILE,
    TERRAIN_ROAD, TERRAIN_RIVER, TERRAIN_GRASS
)
from crossy.player import Player
from crossy.terrain import TerrainManager
from crossy.obstacles import ObstacleManager


class GameState:
    """Manages game state and logic."""

    STATE_START = "start"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        """Initialize game state."""
        self.state = self.STATE_START
        self.player = Player()
        self.terrain_manager = TerrainManager()
        self.obstacle_manager = ObstacleManager()
        self.high_score = self._load_high_score()
        
        # Generate initial obstacles
        self._generate_initial_obstacles()

    def _load_high_score(self):
        """Load high score from file."""
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return int(f.read().strip())
        except (ValueError, IOError):
            pass
        return 0

    def _save_high_score(self):
        """Save high score to file."""
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                f.write(str(self.high_score))
        except IOError:
            pass

    def _generate_initial_obstacles(self):
        """Generate obstacles for all initial terrain rows."""
        for i, row in enumerate(self.terrain_manager.rows):
            if row.terrain_type in (TERRAIN_ROAD, TERRAIN_RIVER):
                self.obstacle_manager.generate_for_row(i, row.terrain_type)

    def start_game(self):
        """Start a new game."""
        self.state = self.STATE_PLAYING
        self.player.reset()
        self.terrain_manager.reset()
        self.obstacle_manager.reset()
        self._generate_initial_obstacles()

    def update(self, dt):
        """
        Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if self.state != self.STATE_PLAYING:
            return

        # Update obstacles
        self.obstacle_manager.update(dt)
        
        # Check if player is on a log and move with it
        current_terrain = self.terrain_manager.get_terrain_at(self.player.y)
        if current_terrain == TERRAIN_RIVER:
            log = self.obstacle_manager.get_log_at_position(self.player.x, self.player.y)
            if log:
                # Move player with log
                old_x = self.player.x
                self.player.x += log.speed * log.direction * dt
                
                # Check if player moved off screen
                if self.player.x < 0 or self.player.x >= GRID_WIDTH:
                    self._game_over()
            else:
                # Player is in water without log - death
                self._game_over()
        
        # Check collision with cars
        if current_terrain == TERRAIN_ROAD:
            if self.obstacle_manager.check_collision_with_car(self.player.x, self.player.y):
                self._game_over()

    def move_player(self, dx, dy):
        """
        Move player by dx, dy.
        
        Args:
            dx: Change in x
            dy: Change in y
        """
        if self.state == self.STATE_PLAYING:
            from crossy.config import TOTAL_ROWS
            self.player.move(dx, dy, GRID_WIDTH, TOTAL_ROWS)

    def _game_over(self):
        """Handle game over."""
        self.state = self.STATE_GAME_OVER
        
        # Update high score
        score = self.player.get_score()
        if score > self.high_score:
            self.high_score = score
            self._save_high_score()

    def restart(self):
        """Restart the game."""
        self.start_game()

    def get_score(self):
        """Get current score."""
        return self.player.get_score()

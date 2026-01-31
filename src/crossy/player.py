"""Player character logic."""

from crossy.config import PLAYER_START_X, PLAYER_START_Y


class Player:
    """Represents the player character."""

    def __init__(self):
        """Initialize the player at starting position."""
        self.x = float(PLAYER_START_X)  # Float to allow smooth log movement
        self.y = PLAYER_START_Y
        self.max_row = PLAYER_START_Y  # Track highest row reached for scoring

    def move(self, dx, dy, grid_width, grid_height):
        """
        Move player by dx, dy if within bounds.
        Player position is snapped to integer grid when jumping.
        
        Args:
            dx: Change in x position
            dy: Change in y position
            grid_width: Maximum grid width
            grid_height: Maximum grid height
        
        Returns:
            bool: True if move was successful
        """
        # Round current position to grid when moving (player jumps to cells)
        new_x = int(self.x) + dx
        new_y = int(self.y) + dy

        # Check bounds
        if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
            self.x = float(new_x)
            self.y = new_y
            
            # Update max row (lower y = further forward)
            if self.y < self.max_row:
                self.max_row = self.y
            
            return True
        return False

    def get_score(self):
        """Get player score based on max row reached."""
        return PLAYER_START_Y - self.max_row

    def reset(self):
        """Reset player to starting position."""
        self.x = float(PLAYER_START_X)
        self.y = PLAYER_START_Y
        self.max_row = PLAYER_START_Y

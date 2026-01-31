"""Terrain generation and management."""

import random
from crossy.config import (
    TERRAIN_GRASS, TERRAIN_ROAD, TERRAIN_RIVER,
    GRID_WIDTH, TOTAL_ROWS
)


class TerrainRow:
    """Represents a single row of terrain."""

    def __init__(self, row_num, terrain_type):
        """
        Initialize a terrain row.
        
        Args:
            row_num: Y coordinate of this row
            terrain_type: Type of terrain (grass, road, river)
        """
        self.row_num = row_num
        self.terrain_type = terrain_type


class TerrainManager:
    """Manages terrain generation."""

    def __init__(self):
        """Initialize terrain manager with a large static grid."""
        self.rows = []
        self._generate_terrain()

    def _generate_terrain_type(self):
        """Randomly generate a terrain type with weighted probabilities."""
        roll = random.random()
        if roll < 0.3:
            return TERRAIN_GRASS
        elif roll < 0.65:
            return TERRAIN_ROAD
        else:
            return TERRAIN_RIVER

    def _generate_terrain(self):
        """Generate all terrain rows upfront."""
        for i in range(TOTAL_ROWS):
            if i >= TOTAL_ROWS - 5:
                # Bottom few rows are safe grass
                self.rows.append(TerrainRow(i, TERRAIN_GRASS))
            else:
                self.rows.append(TerrainRow(i, self._generate_terrain_type()))

    def get_terrain_at(self, grid_y):
        """
        Get terrain type at a specific grid y coordinate.
        
        Args:
            grid_y: Y coordinate in grid space
        
        Returns:
            str: Terrain type or None if out of bounds
        """
        if 0 <= grid_y < len(self.rows):
            return self.rows[grid_y].terrain_type
        return None

    def reset(self):
        """Reset terrain to initial state."""
        self.rows.clear()
        self._generate_terrain()

"""Terrain generation and management."""

import random
from crossy.config import (
    TERRAIN_GRASS, TERRAIN_ROAD, TERRAIN_RIVER, TERRAIN_TRAIN,
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

    def _generate_terrain_type(self, row_num):
        """
        Randomly generate a terrain type with weighted probabilities.
        
        Difficulty ramps up based on row number (lower row = further in game = harder).
        Progress goes from 0.0 (start) to 1.0 (furthest point).
        
        Real Crossy Road starts easy with mostly grass, then gradually introduces
        roads, water, and finally train tracks.
        
        Args:
            row_num: The row number (lower = further progress)
        """
        # Calculate progress: 0.0 at start (high row numbers), 1.0 at furthest point (row 0)
        # Safe zone is last 5 rows, so progress starts from TOTAL_ROWS - 6
        playable_rows = TOTAL_ROWS - 5
        progress = 1.0 - (row_num / playable_rows)
        progress = max(0.0, min(1.0, progress))  # Clamp to [0, 1]
        
        # Base probabilities (early game - balanced start)
        # Grass: 50%, Road: 50%, River: 0%, Train: 0%
        grass_prob = 0.50
        road_prob = 0.50
        river_prob = 0.0
        train_prob = 0.0
        
        # As progress increases, shift probabilities toward harder terrain
        # At max progress (1.0):
        # Grass: 30%, Road: 35%, River: 25%, Train: 10%
        if progress > 0.0:
            # Gradually introduce rivers after 15% progress
            if progress > 0.15:
                river_intro = min(1.0, (progress - 0.15) / 0.35)  # Ramps from 0 to 1 over progress 0.15-0.50
                river_prob = 0.25 * river_intro
            
            # Gradually introduce trains after 35% progress
            if progress > 0.35:
                train_intro = min(1.0, (progress - 0.35) / 0.40)  # Ramps from 0 to 1 over progress 0.35-0.75
                train_prob = 0.10 * train_intro
            
            # Road stays around 35-50%, decreasing slightly as rivers/trains appear
            # This keeps road common throughout while making room for other terrain
            road_prob = 0.50 - (0.15 * progress)  # 50% -> 35%
            
            # Grass decreases to make room for other terrain types
            grass_prob = 1.0 - road_prob - river_prob - train_prob
        
        # Generate terrain based on probabilities
        roll = random.random()
        cumulative = 0.0
        
        cumulative += grass_prob
        if roll < cumulative:
            return TERRAIN_GRASS
        
        cumulative += road_prob
        if roll < cumulative:
            return TERRAIN_ROAD
        
        cumulative += river_prob
        if roll < cumulative:
            return TERRAIN_RIVER
        
        return TERRAIN_TRAIN

    def _generate_terrain(self):
        """Generate all terrain rows upfront with progressive difficulty."""
        for i in range(TOTAL_ROWS):
            if i >= TOTAL_ROWS - 5:
                # Bottom few rows are safe grass (starting area)
                self.rows.append(TerrainRow(i, TERRAIN_GRASS))
            else:
                self.rows.append(TerrainRow(i, self._generate_terrain_type(i)))

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

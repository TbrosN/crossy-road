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

    def _get_progress(self, row_num):
        """
        Calculate progress based on row number.
        
        Args:
            row_num: The row number (lower = further progress)
        
        Returns:
            float: Progress from 0.0 (start) to 1.0 (furthest point)
        """
        playable_rows = TOTAL_ROWS - 5
        progress = 1.0 - (row_num / playable_rows)
        return max(0.0, min(1.0, progress))

    def _get_terrain_probabilities(self, progress):
        """
        Get terrain type probabilities based on progress.
        
        Args:
            progress: Game progress from 0.0 to 1.0
        
        Returns:
            dict: Mapping of terrain type to probability
        """
        # Base probabilities (early game - balanced start)
        # Grass: 50%, Road: 50%, River: 0%, Train: 0%
        grass_prob = 0.50
        road_prob = 0.50
        river_prob = 0.0
        train_prob = 0.0
        
        # As progress increases, shift probabilities toward harder terrain
        if progress > 0.0:
            # Gradually introduce rivers after 15% progress
            if progress > 0.15:
                river_intro = min(1.0, (progress - 0.15) / 0.35)
                river_prob = 0.25 * river_intro
            
            # Gradually introduce trains after 35% progress
            if progress > 0.35:
                train_intro = min(1.0, (progress - 0.35) / 0.40)
                train_prob = 0.10 * train_intro
            
            # Road decreases slightly as rivers/trains appear
            road_prob = 0.50 - (0.15 * progress)
            
            # Grass fills the remainder
            grass_prob = 1.0 - road_prob - river_prob - train_prob
        
        return {
            TERRAIN_GRASS: grass_prob,
            TERRAIN_ROAD: road_prob,
            TERRAIN_RIVER: river_prob,
            TERRAIN_TRAIN: train_prob
        }

    def _pick_terrain_type(self, probabilities):
        """
        Pick a terrain type based on probabilities.
        
        Args:
            probabilities: Dict mapping terrain type to probability
        
        Returns:
            str: Selected terrain type
        """
        roll = random.random()
        cumulative = 0.0
        
        for terrain_type, prob in probabilities.items():
            cumulative += prob
            if roll < cumulative:
                return terrain_type
        
        # Fallback (shouldn't happen if probabilities sum to 1)
        return TERRAIN_GRASS

    def _get_cluster_size(self, terrain_type, progress):
        """
        Get cluster size for a terrain type based on progress.
        
        Dangerous terrain clusters get larger as difficulty increases,
        but stay conservative to avoid overwhelming the player.
        
        Args:
            terrain_type: The type of terrain
            progress: Game progress from 0.0 to 1.0
        
        Returns:
            int: Number of rows in this cluster
        """
        if terrain_type == TERRAIN_GRASS:
            # Grass clusters: 1-2 rows consistently
            return random.randint(1, 2)
        
        elif terrain_type == TERRAIN_ROAD:
            # Road clusters: very conservative scaling
            # Early (progress < 0.3): always 1 row
            # Mid (0.3-0.6): 1-2 rows
            # Late (> 0.6): 1-3 rows
            if progress < 0.3:
                return 1
            elif progress < 0.6:
                return random.randint(1, 2)
            else:
                return random.randint(1, 3)
        
        elif terrain_type == TERRAIN_RIVER:
            # River clusters: similar to roads
            # Early: 1 row, Mid: 1-2, Late: 1-3
            if progress < 0.3:
                return 1
            elif progress < 0.6:
                return random.randint(1, 2)
            else:
                return random.randint(1, 3)
        
        elif terrain_type == TERRAIN_TRAIN:
            # Train clusters: always 1 (trains are deadly)
            return 1
        
        return 1

    def _generate_terrain(self):
        """
        Generate all terrain rows upfront with progressive difficulty.
        
        Terrain is generated in clusters, with grass breaks between
        dangerous terrain types to prevent overwhelming sequences.
        """
        # Start with safe grass rows at the bottom
        safe_rows = 5
        for i in range(TOTAL_ROWS - safe_rows, TOTAL_ROWS):
            self.rows.append(TerrainRow(i, TERRAIN_GRASS))
        
        # Generate terrain in clusters from bottom to top (high row numbers to low)
        current_row = TOTAL_ROWS - safe_rows - 1
        last_terrain_type = TERRAIN_GRASS  # Track previous terrain for spacing
        
        while current_row >= 0:
            progress = self._get_progress(current_row)
            probabilities = self._get_terrain_probabilities(progress)
            terrain_type = self._pick_terrain_type(probabilities)
            
            # If we just had dangerous terrain and picked dangerous terrain again,
            # insert a grass break first (higher chance at low progress)
            is_dangerous = terrain_type in (TERRAIN_ROAD, TERRAIN_RIVER, TERRAIN_TRAIN)
            was_dangerous = last_terrain_type in (TERRAIN_ROAD, TERRAIN_RIVER, TERRAIN_TRAIN)
            
            if is_dangerous and was_dangerous:
                # Insert grass break between dangerous terrain clusters
                # Early game: always insert grass break
                # Late game: 50% chance of grass break
                grass_break_chance = 1.0 - (0.5 * progress)  # 100% -> 50%
                if random.random() < grass_break_chance:
                    # Insert 1-2 rows of grass
                    grass_size = random.randint(1, 2)
                    grass_size = min(grass_size, current_row + 1)
                    for i in range(grass_size):
                        row_num = current_row - i
                        if row_num >= 0:
                            self.rows.append(TerrainRow(row_num, TERRAIN_GRASS))
                    current_row -= grass_size
                    last_terrain_type = TERRAIN_GRASS
                    continue
            
            # Generate the terrain cluster
            cluster_size = self._get_cluster_size(terrain_type, progress)
            cluster_size = min(cluster_size, current_row + 1)
            
            for i in range(cluster_size):
                row_num = current_row - i
                if row_num >= 0:
                    self.rows.append(TerrainRow(row_num, terrain_type))
            
            current_row -= cluster_size
            last_terrain_type = terrain_type
        
        # Sort rows by row_num so they're in correct order
        self.rows.sort(key=lambda r: r.row_num)

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

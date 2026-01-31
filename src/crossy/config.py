"""Game configuration constants."""

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Grid settings
CELL_SIZE = 40
GRID_WIDTH = 20  # Number of cells horizontally
GRID_HEIGHT = 15  # Number of cells vertically (visible on screen)
TOTAL_ROWS = 100  # Total rows in the game world

# Game settings
PLAYER_START_X = GRID_WIDTH // 2
PLAYER_START_Y = TOTAL_ROWS - 3  # Start near the bottom of the world
SCROLL_SPEED = 0.5  # Rows per second that the screen auto-scrolls upward
SCROLL_THRESHOLD = 0.75  # Player position threshold (0.75 = 1/4 from bottom, 3/4 from top)
SCROLL_CATCHUP_SPEED = 3.0  # Extra scroll speed when player is above threshold

# Terrain generation
TERRAIN_GRASS = "grass"
TERRAIN_ROAD = "road"
TERRAIN_RIVER = "river"
TERRAIN_TRAIN = "train"

# Colors (R, G, B)
COLOR_BACKGROUND = (50, 50, 50)
COLOR_GRASS = (34, 139, 34)
COLOR_ROAD = (60, 60, 60)
COLOR_RIVER = (30, 144, 255)
COLOR_TRAIN_TRACK = (80, 60, 40)
COLOR_PLAYER = (255, 255, 0)
COLOR_CAR_RED = (220, 20, 60)
COLOR_CAR_BLUE = (65, 105, 225)
COLOR_CAR_ORANGE = (255, 140, 0)
COLOR_LOG = (139, 69, 19)
COLOR_TREE = (34, 100, 34)
COLOR_TRAIN = (180, 40, 40)
COLOR_TEXT = (255, 255, 255)

# Obstacle settings
CAR_SPEED_MIN = 1.0
CAR_SPEED_MAX = 3.0
LOG_SPEED_MIN = 0.5
LOG_SPEED_MAX = 2.0
TRAIN_SPEED = 8.0  # Trains move fast!
TRAIN_WIDTH = 25  # Very long to cover most of the track
TRAIN_SPAWN_INTERVAL_MIN = 5.0  # Minimum seconds between trains
TRAIN_SPAWN_INTERVAL_MAX = 10.0  # Maximum seconds between trains
TRAIN_WARNING_TIME = 2.0  # Seconds of warning before train appears

# Spawn rates (per row)
CARS_PER_ROW = (2, 5)  # Min, max
LOGS_PER_ROW = (2, 3)  # Min, max (logs are wider now)
TREES_PER_ROW = (0, 4)  # Min, max (trees block movement)
TRAINS_PER_ROW = 1  # Always one train track per train row

# High score file
HIGH_SCORE_FILE = "high_score.txt"

# Debug settings
DEBUG_MODE = False  # Toggle with 'D' key during gameplay
DEBUG_HITBOX_COLOR = (255, 0, 255)  # Magenta for hitbox outlines

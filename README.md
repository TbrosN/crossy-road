# Crossy Road Clone

A simple Crossy Road clone built with Python and Pygame-ce. This was built with AI for 15-113 at CMU on a 1-hour timer.

## Setup

```bash
# Install dependencies
uv sync

# Run the game
uv run crossy
```

## Controls

- **Arrow Keys**: Move player (up, down, left, right)
- **R**: Restart after game over
- **ESC**: Quit

## MVP Features

- Grid-based movement
- Procedural terrain generation (grass, roads, rivers)
- Cars that kill on collision
- Logs that player must ride on rivers
- Score based on distance traveled
- High score persistence

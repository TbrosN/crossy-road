"""Main game entry point and game loop."""

import pygame
from crossy.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, CELL_SIZE,
    GRID_WIDTH, GRID_HEIGHT,
    COLOR_BACKGROUND, COLOR_GRASS, COLOR_ROAD, COLOR_RIVER,
    COLOR_PLAYER, COLOR_TEXT,
    TERRAIN_GRASS, TERRAIN_ROAD, TERRAIN_RIVER
)
from crossy.game import GameState
from crossy.obstacles import Car, Log


class Game:
    """Main game class handling the game loop and rendering."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Crossy Road Clone")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.game_state = GameState()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_state.state == GameState.STATE_START:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.game_state.start_game()
                
                elif self.game_state.state == GameState.STATE_PLAYING:
                    if event.key == pygame.K_UP:
                        self.game_state.move_player(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.game_state.move_player(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.game_state.move_player(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.game_state.move_player(1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                elif self.game_state.state == GameState.STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.game_state.restart()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    def update(self, dt):
        """
        Update game state.
        
        Args:
            dt: Delta time in seconds
        """
        self.game_state.update(dt)

    def render(self):
        """Render the game."""
        self.screen.fill(COLOR_BACKGROUND)
        
        if self.game_state.state == GameState.STATE_START:
            self._render_start_screen()
        elif self.game_state.state == GameState.STATE_PLAYING:
            self._render_game()
        elif self.game_state.state == GameState.STATE_GAME_OVER:
            self._render_game_over()
        
        pygame.display.flip()

    def _render_start_screen(self):
        """Render the start screen."""
        title = self.font.render("CROSSY ROAD CLONE", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "Use ARROW KEYS to move",
            "Avoid cars, ride logs across rivers",
            "",
            "Press SPACE to start"
        ]
        
        y_offset = WINDOW_HEIGHT // 2
        for instruction in instructions:
            text = self.small_font.render(instruction, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        # High score
        high_score_text = self.small_font.render(
            f"High Score: {self.game_state.high_score}",
            True, COLOR_TEXT
        )
        hs_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(high_score_text, hs_rect)

    def _render_game(self):
        """Render the game world."""
        # Calculate offset to center the grid
        offset_x = (WINDOW_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
        offset_y = (WINDOW_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2
        
        # Calculate which rows to render (centered on player)
        player_y = self.game_state.player.y
        camera_start_row = max(0, player_y - GRID_HEIGHT // 2)
        camera_end_row = min(len(self.game_state.terrain_manager.rows), camera_start_row + GRID_HEIGHT)
        
        # Adjust camera if near edges
        if camera_end_row - camera_start_row < GRID_HEIGHT:
            camera_start_row = max(0, camera_end_row - GRID_HEIGHT)
        
        # Render terrain
        for i in range(camera_start_row, camera_end_row):
            row = self.game_state.terrain_manager.rows[i]
            screen_y = (i - camera_start_row) * CELL_SIZE
            
            color = COLOR_GRASS
            if row.terrain_type == TERRAIN_ROAD:
                color = COLOR_ROAD
            elif row.terrain_type == TERRAIN_RIVER:
                color = COLOR_RIVER
            
            rect = pygame.Rect(
                offset_x,
                offset_y + screen_y,
                GRID_WIDTH * CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(self.screen, color, rect)
        
        # Render obstacles
        for obstacle in self.game_state.obstacle_manager.obstacles:
            if camera_start_row <= obstacle.y < camera_end_row:
                screen_y = (obstacle.y - camera_start_row) * CELL_SIZE
                rect = pygame.Rect(
                    offset_x + int(obstacle.x * CELL_SIZE),
                    offset_y + screen_y,
                    int(obstacle.width * CELL_SIZE),
                    CELL_SIZE
                )
                
                # Slightly smaller rect for visual separation
                rect = rect.inflate(-4, -4)
                pygame.draw.rect(self.screen, obstacle.color, rect)
        
        # Render player
        screen_y = (self.game_state.player.y - camera_start_row) * CELL_SIZE
        player_rect = pygame.Rect(
            offset_x + self.game_state.player.x * CELL_SIZE,
            offset_y + screen_y,
            CELL_SIZE,
            CELL_SIZE
        )
        player_rect = player_rect.inflate(-4, -4)
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        
        # Render score
        score_text = self.font.render(
            f"Score: {self.game_state.get_score()}",
            True, COLOR_TEXT
        )
        self.screen.blit(score_text, (10, 10))

    def _render_game_over(self):
        """Render the game over screen."""
        # Render the game state in background (dimmed)
        self._render_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over = self.font.render("GAME OVER", True, COLOR_TEXT)
        go_rect = game_over.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(game_over, go_rect)
        
        # Score
        score = self.game_state.get_score()
        score_text = self.font.render(f"Score: {score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # High score
        if score >= self.game_state.high_score:
            hs_text = self.font.render("NEW HIGH SCORE!", True, (255, 215, 0))
        else:
            hs_text = self.small_font.render(
                f"High Score: {self.game_state.high_score}",
                True, COLOR_TEXT
            )
        hs_rect = hs_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(hs_text, hs_rect)
        
        # Restart prompt
        restart_text = self.small_font.render("Press R to restart", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Run the game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

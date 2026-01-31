"""Main game entry point and game loop."""

import pygame
from crossy.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, CELL_SIZE,
    GRID_WIDTH, GRID_HEIGHT,
    COLOR_BACKGROUND, COLOR_GRASS, COLOR_ROAD, COLOR_RIVER,
    COLOR_PLAYER, COLOR_TEXT, COLOR_TREE,
    TERRAIN_GRASS, TERRAIN_ROAD, TERRAIN_RIVER,
    DEBUG_HITBOX_COLOR
)
from crossy.game import GameState
from crossy.obstacles import Car, Log, Tree


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
        self.debug_mode = False  # Toggle with 'D' key

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
                    elif event.key == pygame.K_d:
                        # Toggle debug mode
                        self.debug_mode = not self.debug_mode
                        print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
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
            "Trees block your path on grass",
            "Press D to toggle debug hitboxes",
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
                pygame.draw.rect(self.screen, obstacle.color, rect)
        
        # Render trees
        for tree in self.game_state.obstacle_manager.trees:
            if camera_start_row <= tree.y < camera_end_row:
                screen_y = (tree.y - camera_start_row) * CELL_SIZE
                rect = pygame.Rect(
                    offset_x + tree.x * CELL_SIZE,
                    offset_y + screen_y,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # Draw tree as a circle for better visual
                center_x = rect.centerx
                center_y = rect.centery
                radius = CELL_SIZE // 3
                pygame.draw.circle(self.screen, tree.color, (center_x, center_y), radius)
        
        # Render player
        screen_y = (self.game_state.player.y - camera_start_row) * CELL_SIZE
        player_rect = pygame.Rect(
            offset_x + self.game_state.player.x * CELL_SIZE,
            offset_y + screen_y,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        
        # Debug mode: render hitboxes
        if self.debug_mode:
            self._render_debug_hitboxes(offset_x, offset_y, camera_start_row, camera_end_row)
        
        # Render score
        score_text = self.font.render(
            f"Score: {self.game_state.get_score()}",
            True, COLOR_TEXT
        )
        self.screen.blit(score_text, (10, 10))
        
        # Debug mode indicator
        if self.debug_mode:
            debug_text = self.small_font.render("DEBUG MODE", True, DEBUG_HITBOX_COLOR)
            self.screen.blit(debug_text, (10, 50))

    def _render_debug_hitboxes(self, offset_x, offset_y, camera_start_row, camera_end_row):
        """
        Render debug hitboxes for player and obstacles.
        
        Args:
            offset_x: X offset for grid rendering
            offset_y: Y offset for grid rendering
            camera_start_row: First visible row
            camera_end_row: Last visible row
        """
        # Draw player hitbox
        player = self.game_state.player
        if camera_start_row <= player.y < camera_end_row:
            left, top, right, bottom = player.get_collision_box()
            screen_y = (top - camera_start_row) * CELL_SIZE
            
            hitbox_rect = pygame.Rect(
                offset_x + left * CELL_SIZE,
                offset_y + screen_y,
                (right - left) * CELL_SIZE,
                (bottom - top) * CELL_SIZE
            )
            pygame.draw.rect(self.screen, DEBUG_HITBOX_COLOR, hitbox_rect, 2)
        
        # Draw obstacle hitboxes
        for obstacle in self.game_state.obstacle_manager.obstacles:
            if camera_start_row <= obstacle.y < camera_end_row:
                left, top, right, bottom = obstacle.get_collision_box()
                screen_y = (top - camera_start_row) * CELL_SIZE
                
                hitbox_rect = pygame.Rect(
                    offset_x + left * CELL_SIZE,
                    offset_y + screen_y,
                    (right - left) * CELL_SIZE,
                    (bottom - top) * CELL_SIZE
                )
                pygame.draw.rect(self.screen, DEBUG_HITBOX_COLOR, hitbox_rect, 2)
        
        # Draw tree hitboxes (trees don't have collision margins)
        for tree in self.game_state.obstacle_manager.trees:
            if camera_start_row <= tree.y < camera_end_row:
                screen_y = (tree.y - camera_start_row) * CELL_SIZE
                
                hitbox_rect = pygame.Rect(
                    offset_x + tree.x * CELL_SIZE,
                    offset_y + screen_y,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, DEBUG_HITBOX_COLOR, hitbox_rect, 2)

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
